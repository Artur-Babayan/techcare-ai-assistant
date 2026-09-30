from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import streamlit as st

from app.config import Settings
from app.kb import load_knowledge_base
from app.llm_client import LLMClientError, OpenAICompatibleClient
from app.retriever import KnowledgeRetriever
from app.service import AssistantService
from app.validators import ResponseValidationError


@st.cache_resource
def build_service() -> AssistantService:
    settings = Settings.from_env()
    items = load_knowledge_base(Path(__file__).parents[1] / "data" / "knowledge_base.json")
    return AssistantService(
        KnowledgeRetriever(items, settings.retrieval_min_score),
        OpenAICompatibleClient(settings.api_base_url, settings.api_key, settings.model, settings.request_timeout),
        settings.retrieval_top_k,
    )


st.set_page_config(page_title="TechCare AI Assistant", layout="wide")
st.title("TechCare · AI Assistant")
left, right = st.columns(2)
with left:
    st.subheader("AmoCRM — диалог")
    message = st.text_area("Сообщение клиента", placeholder="Введите сообщение клиента…", height=160)
    submitted = st.button("Подготовить ответ", type="primary", use_container_width=True)

if submitted:
    if not message.strip():
        st.error("Введите сообщение клиента.")
    else:
        try:
            st.session_state.result = build_service().process(message)
            st.session_state.client_message = message
        except (LLMClientError, ResponseValidationError, ValueError) as exc:
            st.error(f"Не удалось подготовить ответ: {exc}")
        except Exception:
            st.error("Сервис временно недоступен. Попробуйте ещё раз позже.")

result = st.session_state.get("result")
if result:
    with left:
        st.caption("Клиент")
        st.info(st.session_state.client_message)
        st.caption("Черновик AI")
        st.success(result.response.client_reply)
        st.code(result.response.client_reply, language=None)
    with right:
        st.subheader("AI-подсказка менеджеру")
        st.write(result.response.upsell_hint or "Допродажа не требуется.")
        st.code(result.response.upsell_hint, language=None)
        st.caption("Flags")
        st.write(", ".join(result.response.flags))
        st.caption("Used knowledge sources")
        for found in result.retrieved_items:
            item = found.item
            st.markdown(f"**{item.id} · {item.topic}** — score: {found.retrieval_score:.3f}")
            st.write(item.text)
        with st.expander("Debug structured output"):
            st.json(asdict(result.response))
