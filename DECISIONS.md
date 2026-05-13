# Architecture Decisions

## ADR-001: Use Incremental Modernization Instead Of Rewrite
Decision:
Keep the PHP application operational and extract capabilities into Python one by one.

Reason:
Big-bang rewrites carry high business and delivery risk.

## ADR-002: Keep Domain Logic Out Of FastAPI Routes
Decision:
Routes only handle transport concerns and call application services.

Reason:
Business rules must be reusable from API, jobs, and scripts.

## ADR-003: Preserve Raw Readings
Decision:
Store raw smart-meter readings separately from aggregated tables.

Reason:
Supports auditability, debugging, replay, and backfills.

## ADR-004: Enforce Idempotent Ingestion
Decision:
Use `external_id` when present, otherwise `meter_id+timestamp`, to prevent double-counting.

Reason:
Retries are normal in production and must not duplicate consumption.

## ADR-005: Start With PostgreSQL, Defer OLAP Split
Decision:
Use PostgreSQL for this demo and document OLAP expansion as optional future work.

Reason:
Keeps operational complexity low while demonstrating core modernization patterns.
