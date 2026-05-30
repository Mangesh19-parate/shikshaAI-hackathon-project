import os
import re
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

class HybridRetriever:
    def __init__(self, collection_name: str = "ncert_knowledge", qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        self.bm25 = None
        self.documents = []
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except Exception:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=768, # MPNet base size
                    distance=qmodels.Distance.COSINE
                )
            )

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def index_documents(self, chunks: List[Dict[str, Any]]):
        """
        Expects chunks in the format:
        [{"text": "...", "metadata": {"subject": "...", "class": "...", "chapter": "...", "page": ...}}]
        """
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Dense embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Insert to Qdrant
        points = []
        for idx, (emb, text, meta) in enumerate(zip(embeddings, texts, metadatas)):
            payload = {"text": text, **meta}
            points.append(
                qmodels.PointStruct(
                    id=idx,
                    vector=emb.tolist(),
                    payload=payload
                )
            )
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        # Build local BM25 for sparse retrieval (in production, use Qdrant's native sparse vectors)
        # For this prototype, we'll maintain it in memory, but normally we'd save/load it.
        tokenized_corpus = [self._tokenize(text) for text in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.documents = chunks

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top_k chunks using dense + sparse retrieval."""
        
        # Dense Retrieval (Qdrant)
        query_vector = self.embedding_model.encode(query).tolist()
        dense_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k * 2
        )
        dense_hits = {hit.id: hit for hit in dense_results}

        # Sparse Retrieval (BM25)
        bm25_hits = {}
        if self.bm25:
            tokenized_query = self._tokenize(query)
            bm25_scores = self.bm25.get_scores(tokenized_query)
            # Get top_k * 2 indices
            top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k * 2]
            for idx in top_bm25_indices:
                if bm25_scores[idx] > 0:
                    bm25_hits[idx] = bm25_scores[idx]

        # Hybrid Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k = 60
        
        # Add dense ranks
        for rank, (doc_id, hit) in enumerate(dense_hits.items()):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (k + rank + 1))
            
        # Add sparse ranks
        for rank, doc_id in enumerate(bm25_hits.keys()):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (k + rank + 1))
            
        # Sort by RRF score
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Retrieve final documents
        final_results = []
        for doc_id, score in sorted_docs:
            if doc_id in dense_hits:
                hit = dense_hits[doc_id]
                final_results.append({
                    "text": hit.payload["text"],
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                    "score": score
                })
            else:
                doc = self.documents[doc_id]
                final_results.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": score
                })
                
        return final_results
