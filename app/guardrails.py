from __future__ import annotations

import re

from app.models import AssistantResponse, KnowledgeItem
from app.validators import ResponseValidationError


def validate_supported_numbers(response: AssistantResponse, knowledge_items: list[KnowledgeItem]) -> None:
    """Reject numeric claims that are not present in the cited KB sources."""
    number_pattern = r"\d+(?:[–-]\d+)?%?"
    source_numbers = set(re.findall(number_pattern, " ".join(item.text for item in knowledge_items)))
    response_numbers = set(re.findall(number_pattern, f"{response.client_reply} {response.upsell_hint}"))
    if response_numbers - source_numbers:
        raise ResponseValidationError("LLM response contains unsupported numeric facts")
