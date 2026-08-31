from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from rank_bm25 import BM25Okapi

class SemanticSearcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.listings = None

    def build_index(self, df):
        remarks_list = df['remarks'].fillna("").tolist()
        print(f"Encoding {len(remarks_list)} listings...")
        embeddings = self.model.encode(remarks_list)

        # Build FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim) # Inner product for cosine sim
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.listings = df.to_dict(orient='records')

    def search(self, query, top_k=10):
        query_emb = self.model.encode([query])
        faiss.normalize_L2(query_emb)

        scores, indices = self.index.search(query_emb, top_k)
        results = [(self.listings[i], float(scores[0][j])) for j, i in enumerate(indices[0])]
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