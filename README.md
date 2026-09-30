# TechCare AI Assistant

MVP для менеджера TechCare: по сообщению клиента находит факты в локальной базе знаний, готовит ответ и подсказку для уместной допродажи.

## Demo

[▶ Посмотреть демонстрацию работы (MP4)](assets/demo.mp4)

> GitHub откроет ролик на странице файла и позволит воспроизвести его в браузере.



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

## Requirements

- Python 3.12;
- OpenAI-compatible API key;
- для Docker: Docker Engine с Docker Compose.

## Local run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

В `.env` укажите минимум:

```env
API_KEY=sk-your-api-key
```

Запустите интерфейс:

```bash
.venv/bin/streamlit run ui/streamlit_app.py
```

Откройте [http://localhost:8501](http://localhost:8501).

## Docker run

```bash
cp .env.example .env
# add API_KEY to .env
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

## Troubleshooting

- `API key is not configured` — добавьте ключ в `.env`.
- Ошибка API — проверьте `API_BASE_URL`, `MODEL`, ключ и доступный API-баланс.

## Guardrails

- только факты из KB;
- без выдуманных цен;
- `insufficient_information` при недостатке данных;
- controlled upsell;
- обработка агрессивного клиента;
- строгий JSON.

## Production improvements

AmoCRM webhook/API, structured logging, PostgreSQL, feedback loop, prompt A/B tests, embeddings/vector search и observability.
