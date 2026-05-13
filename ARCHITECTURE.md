# Architecture

## Goal
Evolve a legacy PHP energy application into a Python-centered data platform without rewriting the legacy portal.

## System Diagram
Browser  
-> Nginx Reverse Proxy  
-> `/legacy/*` -> PHP Legacy App  
-> `/api/*` and `/docs` -> Python FastAPI Service  
-> PostgreSQL

## Service Boundaries
- `nginx`: single entrypoint and routing split.
- `legacy-php`: UI and legacy interaction layer only.
- `python-service`: validation, ingestion, aggregation, analytics, job orchestration, observability.
- `postgres`: durable storage for raw, rejected, aggregate, quality, and job-run data.

## Python Layering
- `api/routes`: transport layer only.
- `application`: orchestration services.
- `domain`: business rules and pure aggregation/quality logic.
- `infrastructure`: DB/session, logging, metrics.

Route handlers stay thin: validate request -> call application service -> return response.

## Data Model
- `raw_readings`: accepted meter readings (idempotent keys via `external_id` or `meter_id+timestamp`).
- `rejected_readings`: invalid payload + reason.
- `daily_consumption`: aggregated daily totals per meter/day.
- `data_quality_issues`: detected future/duplicate/missing interval issues.
- `job_runs`: job execution status and counters.

## Core Flows
### Ingestion Flow
1. PHP submits payload to `POST /api/readings`.
2. Pydantic + domain validation executes.
3. Duplicate detection enforces idempotency.
4. Accepted record stored in `raw_readings`.
5. Invalid data captured in `rejected_readings` (seed path) or rejected via API response.

### Aggregation Flow
1. `POST /api/jobs/aggregate-daily` triggers job.
2. Raw readings aggregated by UTC day/meter.
3. Upsert to `daily_consumption` (safe re-run).
4. Data-quality checks run.
5. Job metadata written to `job_runs`.

## Observability
- Structured JSON logs
- `x-request-id` correlation
- `GET /api/health`
- `GET /api/metrics`
- Job and quality tables for operational traceability

## Design Principles
- Incremental extraction over rewrite
- Explicit service boundaries
- Idempotency by default
- Raw data preserved for audit/backfill
- Re-runnable jobs and measurable operations
