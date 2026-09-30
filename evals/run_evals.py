from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import re

from app.config import Settings
from app.kb import load_knowledge_base
from app.llm_client import OpenAICompatibleClient
from app.models import ALLOWED_FLAGS, AssistantResponse
from app.retriever import KnowledgeRetriever
from app.service import AssistantService


CASES = [
    ("Сколько занимает установка Windows?", {"kb_005"}, {"no_upsell"}, set()),
    ("Сколько стоит чистка ноутбука? Он сильно греется.", {"kb_002"}, set(), set()),
    ("Почему диагностика такая дорогая?", {"kb_001"}, set(), set()),
    ("Вы ремонтируете iPhone 16 Pro?", set(), {"out_of_scope", "insufficient_information"}, set()),
    ("Вы ужасный сервис! После ремонта всё снова сломалось!", {"kb_009"}, {"aggressive", "no_upsell"}, {"upsell_available"}),
    ("Компьютер тормозит, особенно когда открываю много программ.", {"kb_003", "kb_004", "kb_012"}, set(), set()),
]


def unsupported_numbers(response: AssistantResponse, source_texts: list[str]) -> set[str]:
    allowed = set(re.findall(r"\d+(?:[–-]\d+)?%?", " ".join(source_texts)))
    returned = set(re.findall(r"\d+(?:[–-]\d+)?%?", f"{response.client_reply} {response.upsell_hint}"))
    return returned - allowed


def evaluate_response(response: AssistantResponse, source_texts: list[str], expected_ids: set[str], required: set[str], forbidden: set[str]) -> list[str]:
    errors = []
    if not set(response.flags).issubset(ALLOWED_FLAGS): errors.append("unknown flags")
    if expected_ids and not expected_ids.intersection(response.used_kb_ids): errors.append("expected KB missing")
    if not required.issubset(response.flags): errors.append("required flags missing")
    if forbidden.intersection(response.flags): errors.append("forbidden flags present")
    if unsupported_numbers(response, source_texts): errors.append("unsupported numeric facts")
    return errors


def main() -> None:
    settings = Settings.from_env()
    if not settings.api_key:
        raise SystemExit("API_KEY is required to run live evaluations")
    items = load_knowledge_base(Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json")
    service = AssistantService(
        KnowledgeRetriever(items, settings.retrieval_min_score),
        OpenAICompatibleClient(settings.api_base_url, settings.api_key, settings.model, settings.request_timeout),
        settings.retrieval_top_k,
    )
    passed = 0
    for index, (message, expected_ids, required, forbidden) in enumerate(CASES, start=1):
        result = service.process(message)
        cited_texts = [found.item.text for found in result.retrieved_items if found.item.id in result.response.used_kb_ids]
        errors = evaluate_response(result.response, cited_texts, expected_ids, required, forbidden)
        if errors:
            print(f"FAIL case {index}: {'; '.join(errors)}")
        else:
            passed += 1
            print(f"PASS case {index}")
    print(f"Checks: {passed}/{len(CASES)}")
    print(f"Score: {passed / len(CASES) * 100:.0f}%")

if __name__ == "__main__":
    main()
