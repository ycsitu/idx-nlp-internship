from ..scripts.listing_summarizer import ListingSummarizer, AnswerabilityChecker
import pandas as pd
import json
from rouge_score import rouge_scorer

from ..scripts.query_parser import SchemaValidator
from ..scripts.taxonomy_builder import taxonomy_data
from ..scripts.semantic_search import SemanticSearcher

summarizer = ListingSummarizer()
df = pd.read_csv('../data/processed/listing_sample.csv')
remarks = df['remarks'].fillna("").tolist()

with open('../data/processed/signal_extraction_full.json', 'r', encoding='utf-8') as f:
    entities = json.load(f)

NUM_TEST_CASES = 50

# assuming remarks & entities spreadsheets are ordered the same way
summaries = [summarizer.extractive_summary(remarks[i], entities[i]) for i in range(NUM_TEST_CASES)] #first 10 entriess


# ROUGE-L scores
scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
scores = []
for i in range(NUM_TEST_CASES):
    scores.append(scorer.score(remarks[i], summaries[i])['rougeL'])

print("--ROUGE-L SCORES--")
print("average precision:", sum(s[0] for s in scores)/NUM_TEST_CASES)
print("average recall:", sum(s[1] for s in scores)/NUM_TEST_CASES)
print("average f1:", sum(s[2] for s in scores)/NUM_TEST_CASES)

print("--SAMPLE SUMMARY--\n", remarks[30], summaries[30])

# AnswerabilityChecker Usage: (pasted from week 8 test)
print("--ANSWERABILITY CHECKER--")
queries = ["this is so unrelated yay", "2 bed 3 bath in san diego"]

validator = SchemaValidator()
searcher = SemanticSearcher()
searcher.build_index(remarks)
checker = AnswerabilityChecker(taxonomy_data, validator)
for query in queries:
    print("query:", query)
    can_answer, message = checker.check_pre_query(query)
    if not can_answer:
        print({"error": message, "answerable": False}) #this should be a function lol
        continue
    else:
        print("precheck passed")

    # Execute query...
    results = searcher.search(query, top_k=1) #using semantic searcher is slow :(
    can_answer, message = checker.check_post_query(query, results)
    if not can_answer:
        print({"message": message, "results": []})
    else:
        print("postcheck passed")
        print("result:", results)