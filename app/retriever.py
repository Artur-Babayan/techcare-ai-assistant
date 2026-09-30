from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import KnowledgeItem, RetrievedKnowledgeItem


class KnowledgeRetriever:
    """Small in-memory TF-IDF retriever for the TechCare knowledge base."""

    def __init__(self, items: list[KnowledgeItem], min_score: float = 0.08) -> None:
        if not items:
            raise ValueError("Knowledge retriever requires at least one item")
        if not 0 <= min_score <= 1:
            raise ValueError("min_score must be between 0 and 1")
        self._items = items
        self._min_score = min_score
        self._vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(4, 6), lowercase=True)
        self._matrix = self._vectorizer.fit_transform(self._document(item) for item in items)

    @staticmethod
    def _document(item: KnowledgeItem) -> str:
        return " ".join([item.topic, item.text, " ".join(item.tags)])

    def search(self, query: str, top_k: int) -> list[RetrievedKnowledgeItem]:
        if not query or not query.strip() or top_k <= 0:
            return []
        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix).ravel()
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        return [
            RetrievedKnowledgeItem(item=self._items[index], retrieval_score=float(score))
            for index, score in ranked[:top_k]
            if score >= self._min_score
        ]
