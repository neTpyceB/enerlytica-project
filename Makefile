COMPOSE ?= docker compose
PYTHON_SERVICE ?= python-api

.PHONY: up down logs test lint migrate seed

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down --remove-orphans

logs:
	$(COMPOSE) logs -f --tail=200

test:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) sh -lc "pip install --quiet pytest httpx && PYTHONPATH=/app pytest -q tests"

lint:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) sh -lc "pip install --quiet ruff && ruff check app tests"

migrate:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) alembic upgrade head

seed:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) python -m app.seed
