# Migration Strategy

## Objective
Modernize a legacy PHP energy application safely by moving business capabilities into Python services without disrupting the existing portal.

## Strategy
1. Keep PHP portal live as the user-facing system of record.
2. Introduce Python API behind Nginx with clear route boundaries.
3. Extract one capability at a time (start with smart-meter ingestion).
4. Move validation and processing rules into Python domain/application layers.
5. Keep PHP as a consumer of Python APIs, not as owner of business logic.
6. Add tests and observability for each extracted capability before moving the next one.

## Safety Controls
- Idempotent ingestion to tolerate retries and duplicates.
- Rejected-reading capture for invalid payload auditability.
- Raw data preservation for backfills and forensic analysis.
- Characterization testing to compare legacy behavior and extracted behavior.
- Job run tracking for aggregation reliability and rollback confidence.

## Planned Capability Order
1. Health and runtime wiring.
2. Single reading ingestion.
3. Daily aggregation and analytics queries.
4. Job history and data-quality issue reporting.
5. Metrics and deeper observability.
