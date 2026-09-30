.PHONY: install run test eval docker-build docker-up docker-down

install:
	python3 -m pip install -r requirements.txt

run:
	streamlit run ui/streamlit_app.py

test:
	pytest -q

eval:
	python evals/run_evals.py

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
