from __future__ import annotations

import json
from pathlib import Path

from app.models import KnowledgeItem


class KnowledgeBaseError(ValueError):
    pass


def load_knowledge_base(path: str | Path) -> list[KnowledgeItem]:
    """Load and minimally validate the local knowledge-base JSON file."""
    try:
        raw_items = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeBaseError(f"Unable to load knowledge base: {exc}") from exc

    if not isinstance(raw_items, list):
        raise KnowledgeBaseError("Knowledge base root must be a list")

    items: list[KnowledgeItem] = []
    seen_ids: set[str] = set()
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            raise KnowledgeBaseError(f"Item {index} must be an object")
        expected = {"id", "topic", "text", "tags"}
        if set(raw_item) != expected:
            raise KnowledgeBaseError(f"Item {index} must have exactly {sorted(expected)}")
        item_id = raw_item["id"]
        topic = raw_item["topic"]
        text = raw_item["text"]
        tags = raw_item["tags"]
        if not all(isinstance(value, str) and value.strip() for value in (item_id, topic, text)):
            raise KnowledgeBaseError(f"Item {index} has invalid text fields")
        if not isinstance(tags, list) or not all(isinstance(tag, str) and tag.strip() for tag in tags):
            raise KnowledgeBaseError(f"Item {index} has invalid tags")
        if item_id in seen_ids:
            raise KnowledgeBaseError(f"Duplicate knowledge base id: {item_id}")
        seen_ids.add(item_id)
        items.append(KnowledgeItem(id=item_id, topic=topic, text=text, tags=tags))
    return items
