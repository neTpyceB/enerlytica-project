# Architecture

## Purpose
The system demonstrates incremental modernization of a legacy PHP energy portal by extracting smart-meter business logic into a Python service while keeping the legacy app operational.

## Target Runtime Topology
Browser  
-> Nginx reverse proxy  
-> `/legacy/*` to PHP legacy app  
-> `/api/*` and `/docs` to Python FastAPI service  
-> PostgreSQL for persistence  

## Service Responsibilities
- `Nginx`: single entry point and route split between legacy and modern components.
- `PHP legacy app`: UI and legacy interaction surface; forwards smart-meter operations to Python API.
- `Python FastAPI service`: validation, idempotent ingestion, aggregation, analytics, job orchestration, observability endpoints.
- `PostgreSQL`: raw readings, rejected readings, daily aggregates, job runs, quality issues.

## Architectural Principles
- Incremental extraction over rewrite.
- Thin transport layer; business logic outside route handlers.
- Raw + aggregate storage separation.
- Idempotent ingestion by explicit keys.
- Re-runnable jobs and observable execution.
