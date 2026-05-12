# AGENTS.md

## Purpose
Delivery guide for implementation agents working on this repository.

## Delivery Rules
- Build only requested functionality.
- Keep changes minimal and production-minded.
- Preserve clean boundaries between legacy PHP and Python services.
- Prioritize working end-to-end behavior over optional features.
- Do not add scope that is not explicitly requested.

## Client-Facing Output Policy
- Keep repository deliverables focused on the final application and its public documentation.
- Avoid exposing internal planning details in client-facing documents.

## Internal Context for Agents
- Internal planning and prompt-capture files are stored in `docs/local/`.
- Read `docs/local/` before implementation to align with scope, sequence, and constraints.
- Treat `docs/local/` as operational context for all agents working in this repo.
