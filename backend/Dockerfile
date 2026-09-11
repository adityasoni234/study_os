# StudyOS backend — used by docker-compose.yml (Postgres + pgvector target).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Postgres driver for the compose stack only. requirements.txt deliberately
# stays psycopg-free so the local SQLite path is zero-infra (see README).
RUN pip install --no-cache-dir "psycopg[binary]>=3.2"

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
