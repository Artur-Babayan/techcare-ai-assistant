from app.kb import load_knowledge_base
from app.retriever import KnowledgeRetriever


def build_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(load_knowledge_base("data/knowledge_base.json"), min_score=0.12)


def test_overheating_finds_cleaning() -> None:
    ids = [result.item.id for result in build_retriever().search("ноутбук сильно греется", 3)]
    assert "kb_002" in ids


def test_windows_finds_windows_kb() -> None:
    ids = [result.item.id for result in build_retriever().search("установка windows", 3)]
    assert "kb_005" in ids


def test_irrelevant_query_has_no_results() -> None:
    assert build_retriever().search("квантовые спутники", 3) == []
