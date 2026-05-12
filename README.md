# Enerlytica Modernization Demo

A compact, production-minded demo showing how to modernize a legacy PHP energy portal by extracting smart-meter ingestion, validation, aggregation, and analytics into a Python FastAPI backend.

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
