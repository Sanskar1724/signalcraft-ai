.PHONY: setup api web test seed docker-up docker-down lint

setup:
	python -m venv .venv
	.venv/Scripts/activate && pip install -r requirements.txt || source .venv/bin/activate && pip install -r requirements.txt
	cp -n .env.example .env || copy .env.example .env

api:
	uvicorn apps.api.app.main:app --app-dir . --reload --port 8000

web:
	cd apps/web && npm install && npm run dev

test:
	python -m pytest -q

seed:
	python scripts/seed.py --fresh

docker-up:
	docker compose up --build

docker-down:
	docker compose down

lint:
	ruff check src apps/api 2>/dev/null || echo "ruff not installed"
	black --check src apps/api 2>/dev/null || echo "black not installed"
