from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    api_base_url: str
    api_key: str
    model: str
    retrieval_top_k: int
    retrieval_min_score: float
    request_timeout: float

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            api_base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            api_key=os.getenv("API_KEY", ""),
            model=os.getenv("MODEL", "gpt-4o-mini"),
            retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "3")),
            retrieval_min_score=float(os.getenv("RETRIEVAL_MIN_SCORE", "0.10")),
            request_timeout=float(os.getenv("REQUEST_TIMEOUT", "30")),
        )
