# this is my old week 5 code, moving it here for now and ill fix it later

from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
import json
import time
import numpy as np
from rank_bm25 import BM25Okapi

class SemanticSearcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.listings = None

    def build_index(self, remarks_list):
        print(f"Encoding {len(remarks_list)} listings...")
        embeddings = self.model.encode(remarks_list)

        # Build FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim) # Inner product for cosine sim
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.listings = remarks_list

    def search(self, query, top_k=10):
        query_emb = self.model.encode([query])
        faiss.normalize_L2(query_emb)

        scores, indices = self.index.search(query_emb, top_k)
        results = [(self.listings[i], scores[0][j]) for j, i in enumerate(indices[0])]
        return results
    
class BM25Searcher:
    def __init__(self, df):
        self.bm25 = BM25Okapi([r.split() for r in df['remarks'].fillna("").tolist()])
        self.listings = df.to_dict(orient='records')

    def search(self, query, top_k=10):
        scores = self.bm25.get_scores(query.split())
        top_index = np.argsort(scores)[::-1][:top_k]

        results = [(self.listings[i], float(scores[i])) for i in top_index]
        return results

df = pd.read_csv('../data/processed/listing_sample.csv')

with open('../data/processed/sample_queries.json', 'r', encoding='utf-8') as f:
    queries = json.load(f)["data"]

searcher = SemanticSearcher()
s_results = []
remarks = df['remarks'].fillna("").tolist()
searcher.build_index(remarks)
s_latencies = []

for query in queries:
    start_time = time.time()
    result = searcher.search(query, top_k=1)
    end_time = time.time()
    latency = (end_time - start_time) * 1000

    for text, score in result:
        s_results.append({'method': 'Semantic', 'query': query, 'latency (ms)': latency, 'text': text, 'score': score})
    s_latencies.append(latency)

print("SemanticSearcher Average latency (top_k=1):", sum(s_latencies)/len(s_latencies))

bm25 = BM25Searcher(df)
b_results = []
b_latencies = []

for query in queries:
    start_time = time.time()
    scores = bm25.search(query, top_k=1)
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    
    b_results.append({
        'method' : 'BM25', 
        'query' : query, 
        'latency (ms)' : latency, 
        'text' : text,
        'score' : score
    })
    b_latencies.append(latency)

print("BM25 Average latency (top_k = 1):", sum(b_latencies)/len(b_latencies))

s_latencies = []
s_results = []

for query in queries:
    start_time = time.time()
    result = searcher.search(query, top_k=10)
    end_time = time.time()
    latency = (end_time - start_time) * 1000

    for text, score in result:
        s_results.append({'method': 'Semantic', 'query': query, 'latency (ms)': latency, 'text': text, 'score': score})
    s_latencies.append(latency)

print("SemanticSearcher Average latency (top_k=10):", sum(s_latencies)/len(s_latencies))

b_results = []
b_latencies = []

for query in queries:
    start_time = time.time()
    scores = bm25.search(query, top_k=10)
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    
    b_results.append({
        'method' : 'BM25', 
        'query' : query, 
        'latency (ms)' : latency, 
        'text' : text,
        'score' : score
    })
    b_latencies.append(latency)

print("BM25 Average latency (top_k = 10):", sum(b_latencies)/len(b_latencies))