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
	$(COMPOSE) run --rm $(PYTHON_SERVICE) pytest

lint:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) ruff check .

migrate:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) alembic upgrade head

seed:
	$(COMPOSE) run --rm $(PYTHON_SERVICE) python -m app.seed
