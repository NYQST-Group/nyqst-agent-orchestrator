# Running the Intelli Stack Locally

## Prerequisites
- Docker Desktop running (for postgres, minio, opensearch)
- Python venv at `~/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/.venv`
- Node modules installed in `ui/`

## Services

```bash
# 1. Docker services
cd ~/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126
docker compose up -d
# postgres:5433, minio:9000/9001, opensearch:9200

# 2. Migrations
source .venv/bin/activate
alembic upgrade head

# 3. Backend
uvicorn intelli.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Frontend
cd ui
npm run dev          # normal mode (needs backend)
npm run dev:demo     # demo mode (mock data, no backend needed)
```

## Environment

Key `.env` settings:
- `OPENAI_API_KEY=sk-proj-...`
- `CHAT_MODEL=gpt-5-nano` (cheap for testing; the project key lacks gpt-4o-mini access)
- `EMBEDDING_MODEL=text-embedding-3-small`

## Known Issues

- Docker Desktop can be unstable if Citrix is running — kill `com.docker.vmnetd` and restart Docker Desktop
- Port 8000 conflicts — check with `lsof -ti :8000`
- Backend doesn't auto-reload `.env` changes — must kill and restart uvicorn
