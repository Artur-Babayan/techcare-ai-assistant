import json

import pytest

from app.kb import load_knowledge_base
from app.retriever import KnowledgeRetriever
from app.service import AssistantService


class FakeLLMClient:
    def generate(self, client_message: str, knowledge_items: list[object]) -> str:
        assert client_message == "Сколько стоит установка Windows?"
        assert any(getattr(item, "id") == "kb_005" for item in knowledge_items)
        return json.dumps({"client_reply": "Установка Windows стоит 3000 ₽.", "upsell_hint": "", "used_kb_ids": ["kb_005"], "flags": ["no_upsell"]})


def test_process_runs_retrieval_and_validation() -> None:
    retriever = KnowledgeRetriever(load_knowledge_base("data/knowledge_base.json"), min_score=0.1)
    result = AssistantService(retriever, FakeLLMClient(), top_k=3).process("Сколько стоит установка Windows?")
    assert result.response.used_kb_ids == ["kb_005"]


def test_empty_input_is_rejected() -> None:
    retriever = KnowledgeRetriever(load_knowledge_base("data/knowledge_base.json"))
    with pytest.raises(ValueError):
        AssistantService(retriever, FakeLLMClient(), top_k=3).process("  ")
