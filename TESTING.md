# Testing

## Goal
Protect migration safety and domain correctness with fast, practical test coverage.

## Test Types
### Unit Tests
Location: `python-service/tests/unit`

Covers:
- validation rules
- idempotency behavior
- aggregation logic
- data quality logic
- metrics rendering
- app/bootstrap integrity

### Integration Tests
Location: `python-service/tests/integration`

Covers:
- API flow behavior for readings, jobs, and analytics
- route-to-service contract behavior

### Golden Dataset Tests
Location: `python-service/tests/golden`

Covers:
- fixed input dataset vs expected aggregated output
- transformation stability over time

### Characterization Tests
Location: `python-service/tests/golden/test_characterization_migration.py`

Covers:
- legacy-style daily aggregation parity with Python domain aggregation
- migration safety for extracted calculation behavior

## Run Commands
- Full tests: `make test`
- Lint: `make lint`

## Expected Outcome
- Deterministic pass/fail signal for domain logic and API behavior
- Early detection of regressions in migration-critical transformations
