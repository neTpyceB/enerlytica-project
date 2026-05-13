# Observability

## Goal
Make runtime behavior easy to understand for a small remote team without guessing.

## Health
- Endpoint: `GET /api/health`
- Returns service and database state.

## Logging
- Structured JSON logs from Python service.
- Each log line includes:
  - `timestamp`
  - `level`
  - `logger`
  - `message`
  - `request_id`
- Request correlation uses `x-request-id` header.

## Metrics
- Endpoint: `GET /api/metrics`
- Prometheus-style text format.

### Counters
- `enerlytica_records_received_total`
- `enerlytica_records_accepted_total`
- `enerlytica_records_rejected_total`
- `enerlytica_duplicates_detected_total`
- `enerlytica_aggregation_runs_total`
- `enerlytica_aggregation_failures_total`

### Gauges
- `enerlytica_aggregation_duration_seconds`
- `enerlytica_last_successful_aggregation_timestamp_seconds`
- `enerlytica_data_freshness_seconds`
- `enerlytica_raw_readings_stored_total`
- `enerlytica_rejected_readings_stored_total`

## Database-Backed Operational Visibility
- `job_runs`: status, start/finish, processed/failed counts, message
- `data_quality_issues`: future timestamp, duplicate, missing interval findings

## Operational Checks
1. Verify stack status: `make up`
2. Check service health: `GET /api/health`
3. Run aggregation: `POST /api/jobs/aggregate-daily`
4. Confirm run status: `GET /api/jobs`
5. Review quality issues: `GET /api/data-quality/issues`
6. Review metrics: `GET /api/metrics`
7. Tail logs: `make logs`
