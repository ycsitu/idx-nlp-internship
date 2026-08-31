import nltk
import pandas as pd
import json
from .query_parser import QueryParser

df = pd.read_csv('../data/processed/listing_sample.csv')
remarks = df['remarks'].fillna("").tolist()

with open('../data/processed/signal_extraction_full.json', 'r', encoding='utf-8') as f:
    entities = json.load(f)

with open('../data/processed/sample_queries.json', 'r', encoding='utf-8') as f:
    queries = json.load(f)["data"]

class ListingSummarizer:
    def extractive_summary(self, remarks, entities, num_sentences=2):
        sentences = nltk.sent_tokenize(remarks)

        # Score sentences by entity mentions and position
        scores = []
        for i, sent in enumerate(sentences): #sent short for sentence
            score = 0
            sent_lower = sent.lower()

            # First sentence bonus
            if i == 0:
                score += 2
            
            # Entity mentions
            if str(entities.get('bedrooms')) in sent:
                score += 1
            if str(entities.get('bathrooms')) in sent:
                score += 1
            if str(entities.get('price')) in sent:
                score += 1
            for amenity in entities.get('amenities'):
                if amenity in sent_lower:
                    score += 1
            for keyword in entities.get('location'):
                if keyword in sent_lower:
                    score += 1

            scores.append((score, sent))

        # Return top sentences
        top_sentences = sorted(scores, reverse=True)[:num_sentences]
        return ' '.join(s[1] for s in sorted(top_sentences, key=lambda x: sentences.index(x[1])))
    
class AnswerabilityChecker:
    def __init__(self, taxonomy, schema_validator):
        self.taxonomy = taxonomy
        self.validator = schema_validator
        self.real_estate_keywords = ['house', 'home', 'bed', 'bath','property', 'listing', 'price', 'sqft', 'pool', 'garage']

    def check_pre_query(self, query):
        """Check BEFORE generating SQL"""
        query_lower = query.lower()

        # Check 1: Is this a real estate question?
        has_re_terms = any(kw in query_lower for kw in self.real_estate_keywords)
        if not has_re_terms:
            return False, "This doesn't appear to be a real estate question"

        # Check 2: Does query reference valid data?
        parser = QueryParser()
        filters = parser.parse(query)
        valid, errors = self.validator.validate_query(filters)
        if not valid:
            return False, f"Query references invalid data: {'; '.join(errors)}"

        return True, "Query is answerable"

    def check_post_query(self, query, results_df):
        """Check AFTER executing SQL"""
        if len(results_df) == 0:
            return False, "No listings match your criteria"
        # Check for all-null results (currently does not happen in my implementation)
        # if results_df().all().all():
        #    return False, "Query returned no meaningful data"

        return True, "Results found"