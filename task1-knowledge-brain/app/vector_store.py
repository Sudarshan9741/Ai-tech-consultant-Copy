from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.storage import storage

class VectorStore:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.chunk_matrix = None
        self.chunks: List[Dict[str, Any]] = []
        self.reload()

    def reload(self):
        """Reload all active chunks from storage and fit the vectorizer."""
        self.chunks = storage.get_all_active_chunks()
        if not self.chunks:
            self.vectorizer = None
            self.chunk_matrix = None
            return

        corpus = [
            f"{c['title']} {c['title']} {c['chunk_text']}" 
            for c in self.chunks
        ]
        
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
            token_pattern=r"(?u)\b[\w-]+\b"
        )
        self.chunk_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for chunks most semantically relevant to query."""
        if not self.chunks or self.vectorizer is None or self.chunk_matrix is None:
            return []

        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        try:
            query_vec = self.vectorizer.transform([cleaned_query])
            scores = cosine_similarity(query_vec, self.chunk_matrix)[0]
        except Exception:
            return []

        # Sort indices by score descending
        ranked_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in ranked_indices[:top_k]:
            score = float(scores[idx])
            if score <= 0.0:
                continue
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk["id"],
                "article_url": chunk["article_url"],
                "title": chunk["title"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["chunk_text"],
                "images": chunk.get("images", []),
                "score": round(score, 4)
            })
        return results

vector_store = VectorStore()
