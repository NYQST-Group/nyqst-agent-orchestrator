# INTELLI Demo - Document Intelligence Platform

**Clean demo branch** - contains only the files needed to run the working demo.

## What This Demo Shows

A NotebookLM-style document workspace built on:
- **Versioned substrate**: immutable artifacts + manifests (snapshots) + mutable pointers (HEADs)
- **Run trace**: every operation logged as run events (full audit trail)
- **RAG Q&A**: upload docs → index → ask questions with sources

## Quick Start

```bash
# 1. One-command startup (validates + runs)
bash scripts/dev/validate.sh

# 2. Interactive demo (keeps running until Ctrl+C)
bash scripts/dev/run.sh
```

Then:
- Open http://localhost:3011/
- Click "Demo Login"
- Create a notebook (+)
- Upload files
- (Optional) Index → Ask questions

## Requirements

- Docker + Docker Compose
- Python 3.11+
- Node.js 18+
- (Optional) `OPENAI_API_KEY` in `.env` for RAG index/ask

## What's Included

**Root:**
- `.env.example` - config template
- `docker-compose.yml` - Postgres + MinIO
- `pyproject.toml` - Python deps
- `alembic.ini` - DB migrations config

**Backend (`src/intelli/`):**
- API endpoints: auth, artifacts, manifests, pointers, runs, RAG
- Services: substrate (artifact/manifest/pointer), runs (ledger), RAG
- DB models: auth, substrate, runs, rag_chunks
- Storage: local + S3-compatible (MinIO)

**UI (`ui/src/`):**
- Login + workbench layout
- Notebook panel (upload/index/ask)
- Viewers: artifact, manifest, pointer, run timeline
- Real-time updates via SSE

**Scripts (`scripts/dev/`):**
- `run.sh` - start everything (infra + backend + UI)
- `validate.sh` - validate each layer (infra → migrations → backend → API → UI)
- `smoke_api.py` - API smoke test (auth + substrate + RAG)

**Docs:**
- `docs/STARTUP_SEQUENCE.md` - detailed startup/troubleshooting

## API Docs

http://localhost:8002/docs (when backend running)

## What's NOT Included

This is a clean demo branch. The following are intentionally excluded:
- Analysis/research markdown files
- Unused agent/workflow code
- Schema definitions not used by the demo
- Test fixtures

For the full development repo, see the `main` or `merged-branch` branches.

## Architecture

```
User uploads file
  ↓
Creates Artifact (immutable, content-addressed)
  ↓
Creates Manifest (snapshot of notebook state)
  ↓
Advances Pointer (notebook "HEAD" → new manifest)
  ↓
All logged as Run Events (audit trail)
```

Optional RAG flow:
```
Index notebook
  ↓
Chunks + embeddings → pgvector
  ↓
Ask question
  ↓
Retrieve relevant chunks
  ↓
LLM generates answer + sources
```

## Ports

- Backend API: 8002 (configurable via `INTELLI_API_PORT`)
- UI: 3011 (configurable via `INTELLI_UI_PORT`)
- Postgres: 5433
- MinIO: 9000 (console: 9001)

## Status

✅ Working demo as of 2026-01-24

See git tag: `milestone-demo-working-2026-01-24`
