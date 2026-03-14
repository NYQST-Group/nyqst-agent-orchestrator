---
document_id: DEVELOPER-SETUP
version: 1
date: 2026-03-14
status: DRAFT — local development environment specification
gap_resolved: GAP-041
---

# Developer Setup Guide — NYQST DocuIntelli

This document specifies the local development environment for NYQST DocuIntelli. It covers prerequisites, docker-compose startup sequence, database initialization, test data seeding, and local observability tooling.

**Target audience**: Engineers onboarding to any track (Backend / Frontend / Platform / DevOps / Domain).

---

## 1. Prerequisites

Run the prerequisites check before anything else:

```bash
# Required tools
python --version    # 3.12+
node --version      # 20+
docker --version    # 24+
docker compose version  # 2.20+
git --version

# Required environment files
ls .env             # Must exist — copy from .env.example if not
ls .env.test        # Must exist for test runs — copy from .env.example.test
```

### .env.example Variables

All required environment variables with explanations:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intelli
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/intelli

# Redis / ARQ
REDIS_URL=redis://localhost:6379/0

# MinIO (S3-compatible)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=intelli-artifacts

# OpenSearch
OPENSEARCH_URL=http://localhost:9200

# Langfuse (observability)
LANGFUSE_HOST=http://localhost:3010
LANGFUSE_PUBLIC_KEY=<from langfuse UI after startup>
LANGFUSE_SECRET_KEY=<from langfuse UI after startup>

# OpenAI
OPENAI_API_KEY=sk-...

# Stripe (test mode)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Brave Search
BRAVE_SEARCH_API_KEY=BSA...

# Jina Reader
JINA_API_KEY=jina_...

# Auth
JWT_SECRET=<generate with: openssl rand -hex 32>
API_KEY_SALT=<generate with: openssl rand -hex 16>

# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

---

## 2. Docker Compose Startup Sequence

Start services in this order to avoid dependency failures:

```bash
# Step 1: Core infrastructure (PostgreSQL, Redis, MinIO)
docker compose up -d postgres redis minio

# Wait for PostgreSQL to be healthy
docker compose ps postgres  # Should show "healthy"

# Step 2: Search + graph
docker compose up -d opensearch neo4j

# Step 3: Observability (optional but recommended)
docker compose --profile observability up -d

# Step 4: Validate all services are running
docker compose ps
```

### Validation Checks

After startup, verify each service:

```bash
# PostgreSQL
psql $DATABASE_URL_SYNC -c "SELECT version();"

# Redis
redis-cli -u $REDIS_URL ping  # Should return PONG

# MinIO
curl http://localhost:9000/minio/health/live  # Should return 200

# OpenSearch
curl http://localhost:9200/_cluster/health  # Should return status: green or yellow

# Langfuse (if started)
curl http://localhost:3010/api/public/health  # Should return {"status":"ok"}
```

---

## 3. Backend Initialization

```bash
cd ~/NYQST-DocuIntelli-Build

# Create virtual environment (one-time)
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-dev.txt

# Run database migrations
.venv/bin/alembic upgrade head

# Verify migration state
.venv/bin/alembic current  # Should show latest migration head

# Start the FastAPI server
.venv/bin/uvicorn src.intelli.main:app --reload --port 8000

# Start the ARQ worker (separate terminal)
.venv/bin/python -m src.intelli.core.worker
```

---

## 4. Frontend Initialization

```bash
cd ~/NYQST-DocuIntelli-Build/ui

# Install dependencies (one-time)
npm install

# Start the Vite dev server
npm run dev  # http://localhost:5173
```

---

## 5. Test Data Seeding

```bash
# Seed a demo tenant, user, and sample conversations
.venv/bin/python scripts/seed_demo_data.py

# What this creates:
# - Tenant: "NYQST Demo" (tenant_id: demo-tenant-001)
# - User: demo@nyqst.ai (API key: demo-api-key-001)
# - 3 sample conversations with run history

# Verify seeding
.venv/bin/python -c "
from src.intelli.core.database import get_sync_session
from src.intelli.models import Tenant
session = next(get_sync_session())
print(session.query(Tenant).count(), 'tenants')
"
```

**Note**: The seed script does not exist yet — this is a P0 task. It should be created as part of the initial platform setup.

---

## 6. Running Tests

```bash
# Unit tests (fast, no external services needed)
.venv/bin/python -m pytest tests/unit/ -q

# Integration tests (requires docker-compose services running)
.venv/bin/python -m pytest tests/integration/ -q

# Frontend tests
cd ui && npm run test

# TypeScript type check
cd ui && npx tsc --noEmit

# Lint (Python)
.venv/bin/python -m ruff check src/ tests/

# All checks (pre-commit equivalent)
make check  # Runs: pytest unit, tsc, ruff check
```

---

## 7. Local Langfuse + LangSmith Studio

### Langfuse (local traces)

After starting with `--profile observability`:

1. Open http://localhost:3010
2. Create a project called `nyqst-local`
3. Copy the public key and secret key into `.env`
4. Traces will appear automatically when you run research workflows

### LangSmith Studio (graph debugging)

LangSmith Studio is a cloud tool (free tier). To use it:

```bash
# Add to .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...  # From https://smith.langchain.com/
LANGCHAIN_PROJECT=nyqst-local

# View graph structure
.venv/bin/python -c "
from src.intelli.graphs.research import ResearchAssistantGraph
graph = ResearchAssistantGraph()
print(graph.get_graph().draw_mermaid())
"
```

---

## 8. Mock API Keys for Development

If you do not have live API keys for Brave Search or Stripe, use the following mock setup:

### Brave Search Mock

```bash
# Set in .env
BRAVE_SEARCH_API_KEY=mock
BRAVE_SEARCH_MOCK=true  # Enables mock responses in src/intelli/mcp/search.py
```

Mock responses return 3 pre-defined search results for any query. Sufficient for testing the research pipeline without consuming Brave API credits.

### Stripe Mock

```bash
# Use Stripe CLI for local webhook testing
stripe listen --forward-to localhost:8000/api/v1/billing/webhook

# Stripe test mode keys work in development without additional setup
# Test card: 4242 4242 4242 4242, any future date, any CVC
```

---

## 9. Common Issues

| Issue | Fix |
|-------|-----|
| `MissingGreenlet` error in async SQLAlchemy | Ensure `expire_on_commit=False` on `async_sessionmaker` (DEC-051) |
| ARQ worker starts but jobs never execute | Fix `WorkerSettings.functions` initialization (GAP-023 — move WorkerSettings to separate module loaded after job definitions) |
| Langfuse traces not appearing | Check `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` in `.env` |
| Migration drift | Run `alembic check` — if drift detected, run `alembic upgrade head` |
| OpenSearch connection refused | Wait 60 seconds after startup; OpenSearch takes longer than PostgreSQL to become ready |

---

*Created: 2026-03-14. Resolves GAP-041 (developer experience tooling spec). Seed script (Section 5) requires implementation as a P0 task.*
