# TechCare AI Assistant

MVP для менеджера TechCare: по сообщению клиента находит факты в локальной базе знаний, готовит ответ и подсказку для уместной допродажи.

## Architecture

Client message → TF-IDF retrieval → relevant KB → LLM → JSON validation → UI

## Why TF-IDF

В базе всего 12 записей, поэтому vector database добавила бы лишнюю сложность. При production-scale можно перейти на embeddings с pgvector или Qdrant.

## Features

- OpenAI-compatible HTTP client без SDK;
- строгая валидация JSON и KB IDs;
- запрет неподтверждённых фактов и контролируемый upsell;
- CRM-подобный Streamlit интерфейс;
- unit tests и набор eval cases.

## Project structure

`app/` — доменная логика, retrieval, LLM и validation; `ui/` — Streamlit; `data/` — KB; `tests/` — unit tests; `evals/` — evaluation checks.

## Local run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/streamlit run ui/streamlit_app.py
```

## Docker run

```bash
cp .env.example .env
docker compose up --build
```

## Tests

```bash
.venv/bin/pytest -q
```

## Evals

```bash
.venv/bin/python evals/run_evals.py
```

## Guardrails

- только факты из KB;
- без выдуманных цен;
- `insufficient_information` при недостатке данных;
- controlled upsell;
- обработка агрессивного клиента;
- строгий JSON.

## Production improvements

AmoCRM webhook/API, structured logging, PostgreSQL, feedback loop, prompt A/B tests, embeddings/vector search и observability.
