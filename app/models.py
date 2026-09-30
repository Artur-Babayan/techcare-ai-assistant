from __future__ import annotations

from dataclasses import dataclass


ALLOWED_FLAGS = frozenset(
    {
        "insufficient_information",
        "aggressive",
        "out_of_scope",
        "upsell_available",
        "no_upsell",
    }
)


@dataclass(frozen=True, slots=True)
class KnowledgeItem:
    id: str
    topic: str
    text: str
    tags: list[str]


@dataclass(frozen=True, slots=True)
class RetrievedKnowledgeItem:
    item: KnowledgeItem
    retrieval_score: float


@dataclass(frozen=True, slots=True)
class AssistantResponse:
    client_reply: str
    upsell_hint: str
    used_kb_ids: list[str]
    flags: list[str]


@dataclass(frozen=True, slots=True)
class AssistantResult:
    response: AssistantResponse
    retrieved_items: list[RetrievedKnowledgeItem]
