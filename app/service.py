from __future__ import annotations

from typing import Protocol

from app.models import AssistantResult, KnowledgeItem
from app.retriever import KnowledgeRetriever
from app.guardrails import validate_supported_numbers
from app.validators import parse_llm_json, validate_assistant_response


class LLMGenerator(Protocol):
    def generate(self, client_message: str, knowledge_items: list[KnowledgeItem]) -> str: ...


class AssistantService:
    def __init__(self, retriever: KnowledgeRetriever, llm_client: LLMGenerator, top_k: int) -> None:
        self._retriever = retriever
        self._llm_client = llm_client
        self._top_k = top_k

    def process(self, client_message: str) -> AssistantResult:
        if not client_message or not client_message.strip():
            raise ValueError("Сообщение клиента не должно быть пустым")
        retrieved_items = self._retriever.search(client_message, self._top_k)
        knowledge_items = [result.item for result in retrieved_items]
        raw_response = self._llm_client.generate(client_message.strip(), knowledge_items)
        payload = parse_llm_json(raw_response)
        response = validate_assistant_response(payload, {item.id for item in knowledge_items})
        cited_items = [item for item in knowledge_items if item.id in response.used_kb_ids]
        validate_supported_numbers(response, cited_items)
        return AssistantResult(response=response, retrieved_items=retrieved_items)
