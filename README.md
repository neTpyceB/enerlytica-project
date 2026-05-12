# Enerlytica Modernization Demo

A compact, production-minded demo showing how to modernize a legacy PHP energy portal by extracting smart-meter ingestion, validation, aggregation, and analytics into a Python FastAPI backend.

## Core Message
This demo shows how to safely evolve a legacy PHP energy application into a modern Python-based data platform using incremental extraction, clear service boundaries, validation, observability, tests, and production-minded engineering.

## What This Project Demonstrates
- Incremental modernization instead of big-bang rewrite.
- Legacy PHP portal kept operational.
- Clean API boundary to Python business services.
- Idempotent smart-meter ingestion.
- Reliable daily aggregation and data-quality visibility.
- Production-minded testing, observability, and documentation.

## Intended Demo Outcome
- A working legacy portal at `/legacy/`.
- A working Python API at `/api/*` and docs at `/docs`.
- End-to-end flow from reading submission to daily consumption analytics.

## Audience
This repository is structured as a client-facing modernization demo suitable for technical leadership review.

## Supporting Documents
- [ARCHITECTURE.md](/Users/vadimsduboiss/Codebase/enerlytica-project/ARCHITECTURE.md)
- [MIGRATION_STRATEGY.md](/Users/vadimsduboiss/Codebase/enerlytica-project/MIGRATION_STRATEGY.md)
