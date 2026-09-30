from __future__ import annotations

import json

from app.models import ALLOWED_FLAGS, AssistantResponse


class ResponseValidationError(ValueError):
    pass


def parse_llm_json(raw_response: str) -> dict[str, object]:
    cleaned = raw_response.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        fence_parts = cleaned.split("\n", 1)
        if len(fence_parts) != 2:
            raise ResponseValidationError("LLM response has an invalid Markdown fence")
        cleaned = fence_parts[1].rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ResponseValidationError("LLM response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ResponseValidationError("LLM response must be a JSON object")
    return parsed


def validate_assistant_response(payload: dict[str, object], allowed_kb_ids: set[str]) -> AssistantResponse:
    expected_fields = {"client_reply", "upsell_hint", "used_kb_ids", "flags"}
    if set(payload) != expected_fields:
        raise ResponseValidationError("LLM response has unexpected or missing fields")
    client_reply, upsell_hint = payload["client_reply"], payload["upsell_hint"]
    kb_ids, flags = payload["used_kb_ids"], payload["flags"]
    if not isinstance(client_reply, str) or not client_reply.strip():
        raise ResponseValidationError("client_reply must be a non-empty string")
    if not isinstance(upsell_hint, str):
        raise ResponseValidationError("upsell_hint must be a string")
    if not isinstance(kb_ids, list) or not all(isinstance(item, str) for item in kb_ids):
        raise ResponseValidationError("used_kb_ids must be a list of strings")
    if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
        raise ResponseValidationError("flags must be a list of strings")
    if not set(kb_ids).issubset(allowed_kb_ids):
        raise ResponseValidationError("LLM used an unavailable knowledge base ID")
    if not set(flags).issubset(ALLOWED_FLAGS):
        raise ResponseValidationError("LLM returned an unsupported flag")
    if len(flags) != len(set(flags)):
        raise ResponseValidationError("LLM returned duplicate flags")
    if {"upsell_available", "no_upsell"}.issubset(flags):
        raise ResponseValidationError("LLM returned contradictory upsell flags")
    return AssistantResponse(client_reply=client_reply.strip(), upsell_hint=upsell_hint.strip(), used_kb_ids=kb_ids, flags=flags)
