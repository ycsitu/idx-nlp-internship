import pandas as pd
import json

from .query_parser import QueryParser, SchemaValidator
from .semantic_search import SemanticSearcher, BM25Searcher
from .entity_extractor import EntityExtractor
from .signal_extractor import SignalExtractor
from .compliance_checker import ComplianceChecker
from .listing_summarizer import ListingSummarizer, AnswerabilityChecker
#from .intent_classifer import IntentClassifier
from .taxonomy_builder import taxonomy_data

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from functools import lru_cache

app = FastAPI(title="Real Estate NLP API")

df = pd.read_csv('../data/processed/cleaned_listing.csv')

with open('../data/processed/taxonomy.json', 'r', encoding='utf-8') as f:
    taxonomy = json.load(f)["terms"]

with open('../data/processed/signal_extraction_full.json', 'r', encoding='utf-8') as f:
    entities = json.load(f)

query_parser = QueryParser()

semantic_searcher = SemanticSearcher()
semantic_searcher.build_index(df)
BM25_searcher = BM25Searcher(df)

# intent classifier
'''
intent_classifier = IntentClassifier()
queries = [item for item in queries_buyerintent['query']]
labels = [item for item in queries_buyerintent['intent']]
intent_classifier.train(queries, labels)'''

entity_extractor = EntityExtractor()
listing_summarizer = ListingSummarizer()
#schema_validator = SchemaValidator()
compliance_checker = ComplianceChecker()
#answerability_checker = AnswerabilityChecker(taxonomy, schema_validator)
signal_extractor = SignalExtractor(taxonomy_data, entity_extractor)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: bool = True

class SearchResponse(BaseModel):
    query: str
    results: list
    count: int

def apply_filters(results, filters):
    filtered_results = []
    for result in results:
        if 'bedrooms_min' in filters and result[0]['beds'] < filters['bedrooms_min']:
            continue
        if 'bedrooms' in filters and result[0]['beds'] != filters['bedrooms']:
            continue
        if 'bathrooms_min' in filters and result[0]['baths'] < filters['bathrooms_min']:
            continue
        if 'bathrooms' in filters and result[0]['baths'] != filters['bathrooms']:
            continue
        if 'price_max' in filters and result[0]['price'] > filters['price_max']:
            continue
        if 'city' in filters and result[0]['L_City'].lower() != filters['city'].lower():
            continue
        # no amenities
        filtered_results.append(result)

    return filtered_results
    

@lru_cache(maxsize=128)
def cache_search(query: str, top_k: int):
    return semantic_searcher.search(query, top_k)

@app.post("/semantic_search", response_model=SearchResponse)
async def search_listings(request: Request, search_request: SearchRequest):

    # Get semantic results
    results = cache_search(search_request.query, search_request.top_k)

    if (search_request.filters):
        results = apply_filters(results, query_parser.parse(search_request.query))

    return SearchResponse(
        query=search_request.query,
        results=results,
        count=len(results)
    )

@app.post("/BM25_search", response_model=SearchResponse)
async def search_listings(request: Request, search_request: SearchRequest):
    results = BM25_searcher.search(search_request.query, search_request.top_k)

    if (search_request.filters):
        results = apply_filters(results, query_parser.parse(search_request.query))
        
    return SearchResponse(
        query=search_request.query,
        results=results,
        count=len(results)
    )

@app.post("/parse_query")
async def parse_query(request: SearchRequest):
    result = query_parser.parse(request.query)
    return {"query": request.query, "parsed_query": result}

@app.post("/extract_entities")
async def extract_entities(request: SearchRequest):
    entities = entity_extractor.extract_all(request.query)
    return {"query": request.query, "entities": entities}

@app.post("/summarize")
async def summarize(remarks: str):
    entities = {
            'bedrooms': entity_extractor.extract_bedrooms(remarks),
            'bathrooms': entity_extractor.extract_bathrooms(remarks),
            'price': entity_extractor.extract_price(remarks),
            'sqft': entity_extractor.extract_sqft(remarks),
            'amenities': signal_extractor._match_amenities(remarks),
            'condition': signal_extractor._extract_category(remarks, signal_extractor.condition_patterns),
            'financing': signal_extractor._extract_category(remarks, signal_extractor.financing_patterns),
            'location': signal_extractor._extract_category(remarks, signal_extractor.location_patterns)
        }
    summary = listing_summarizer.extractive_summary(remarks, entities)
    return {"listing": remarks, "summary": summary}

@app.post("/check_compliance")
async def check_compliance(posting: str):
    compliance = compliance_checker.check_listing(posting.description)
    return {"listing": posting.description,
            "compliant": compliance["compliant"],
            "num_violations": compliance["num_violations"],
            "violations_list": compliance["violations_list"]}