FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir alembic fastapi uvicorn[standard] sqlalchemy psycopg[binary]

COPY app /app/app
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini
