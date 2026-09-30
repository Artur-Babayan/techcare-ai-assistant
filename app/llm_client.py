from __future__ import annotations

from typing import Any

import httpx

from app.models import KnowledgeItem
from app.prompts import SYSTEM_PROMPT, build_user_prompt


class LLMClientError(RuntimeError):
    pass


class OpenAICompatibleClient:
    def __init__(self, api_base_url: str, api_key: str, model: str, timeout: float) -> None:
        self._url = f"{api_base_url.rstrip('/')}/chat/completions"
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def generate(self, client_message: str, knowledge_items: list[KnowledgeItem]) -> str:
        if not self._api_key:
            raise LLMClientError("API key is not configured")
        payload: dict[str, Any] = {
            "model": self._model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(client_message, knowledge_items)},
            ],
        }
        try:
            response = httpx.post(
                self._url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMClientError(f"LLM request failed: {exc}") from exc
        if not isinstance(content, str) or not content.strip():
            raise LLMClientError("LLM returned an empty response")
        return content
