# Enerlytica Modernization Demo

A compact production-minded demo showing how to modernize a legacy PHP energy portal by extracting smart-meter processing, validation, analytics, and scheduled jobs into a modern Python FastAPI backend.

## Why This Exists
This project demonstrates incremental modernization, not a big-bang rewrite. The legacy PHP app stays live while new business capabilities move into Python behind stable internal APIs.

## What It Demonstrates
- Incremental PHP-to-Python modernization
- Nginx reverse proxy routing
- Smart-meter ingestion with validation and idempotency
- Raw + aggregate persistence in PostgreSQL
- Re-runnable daily aggregation job
- Data-quality issue detection
- Structured logs, request correlation ID, health checks, metrics
- Unit, integration, golden dataset, and characterization tests
- Docker Compose local deployment

## Runtime Topology
Browser -> Nginx -> PHP (`/legacy/*`) and FastAPI (`/api/*`, `/docs`) -> PostgreSQL

## Tech Stack
- Nginx
- PHP 8 (legacy-style app)
- Python 3.12 + FastAPI + Pydantic v2
- SQLAlchemy 2.x + Alembic
- PostgreSQL
- pytest + ruff
- Docker Compose

## Quick Start
1. Copy env template (optional):
   - `cp .env.example .env`
2. Start stack:
   - `make up`
3. Apply migrations:
   - `make migrate`
4. Seed demo data:
   - `make seed`

## Local URLs
- Legacy portal: [http://localhost/legacy/](http://localhost/legacy/)
- API docs: [http://localhost/docs](http://localhost/docs)
- Health: [http://localhost/api/health](http://localhost/api/health)
- Metrics: [http://localhost/api/metrics](http://localhost/api/metrics)

## Key API Endpoints
- `POST /api/readings`
- `GET /api/health`
- `POST /api/jobs/aggregate-daily`
- `GET /api/jobs`
- `GET /api/data-quality/issues`
- `GET /api/meters/{meter_id}/daily-consumption`
- `GET /api/customers/{customer_id}/daily-consumption`
- `GET /api/metrics`

## Common Commands
- `make up`
- `make down`
- `make logs`
- `make migrate`
- `make seed`
- `make test`
- `make lint`

## 5-Minute Demo Script
1. Open [http://localhost/legacy/](http://localhost/legacy/) and explain this is the legacy system kept alive.
2. Go to submit page and create a reading from PHP.
3. Explain PHP forwards to Python API.
4. Re-submit same reading and show duplicate/idempotent result.
5. Submit an invalid payload and show rejection.
6. Trigger `POST /api/jobs/aggregate-daily`.
7. Show daily consumption from dashboard/API.
8. Show `GET /api/jobs` for run status and processed counts.
9. Show `GET /api/data-quality/issues`.
10. Show `GET /api/metrics` and structured logs with request IDs.
11. Show `make test` output as safety net.
12. Close with migration strategy and tradeoffs.

## What This Demonstrates For Enerlytica
- I can modernize safely without stopping legacy operations.
- I extract business logic into clear Python boundaries.
- I treat data quality, idempotency, and timezone correctness as first-class.
- I make jobs observable and re-runnable.
- I use tests and characterization checks to reduce migration risk.
- I optimize for pragmatic delivery, not architecture theater.

## Documentation
- [ARCHITECTURE.md](/Users/vadimsduboiss/Codebase/enerlytica-project/ARCHITECTURE.md)
- [MIGRATION_STRATEGY.md](/Users/vadimsduboiss/Codebase/enerlytica-project/MIGRATION_STRATEGY.md)
- [OBSERVABILITY.md](/Users/vadimsduboiss/Codebase/enerlytica-project/OBSERVABILITY.md)
- [TESTING.md](/Users/vadimsduboiss/Codebase/enerlytica-project/TESTING.md)
- [DECISIONS.md](/Users/vadimsduboiss/Codebase/enerlytica-project/DECISIONS.md)
