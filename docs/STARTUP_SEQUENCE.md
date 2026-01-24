# Validated Startup Sequence (Dev)

Goal: start the full local stack **in a known-good order**, validating each layer before moving to the next so integration issues surface early (and locally).

## One-command validation (recommended)

Run the automated sequence (infra → migrations → backend health → API smoke → UI build):

```bash
bash scripts/dev/validate.sh
```

This ends with clear “pass/fail” output and stops immediately on the first failure.

Note: `scripts/dev/validate.sh` will run RAG smoke steps if `OPENAI_API_KEY` is set (in `.env` is fine). To **fail** if RAG can’t run, set `INTELLI_REQUIRE_RAG=1`.

## Interactive demo (run the app)

This starts infra + migrations, then keeps the backend and UI running until you press Ctrl+C:

```bash
bash scripts/dev/run.sh
```

## Manual sequence (with explicit checks)

### 0) Git update (optional)

```bash
git fetch --all --prune
git status -sb

# If you're behind your upstream branch (and have no local work to protect):
git pull --rebase
```

### 1) Prereqs / ports

- Required: `docker` + `docker compose`, `python3`, `node` + `npm`, `curl`
- Ports used by default:
  - Backend: `8000`
  - UI: `3000`
  - Postgres: `5433` (configurable via `INTELLI_POSTGRES_PORT` in `docker-compose.yml`)
  - MinIO: `9000` (+ console `9001`)
- Note: `docker-compose.yml` includes an optional Langfuse service that also uses `3000` (only start that profile if you change ports).

Overrides:
- Backend port: set `INTELLI_API_PORT` (used by `scripts/dev/validate.sh` and as the default for `scripts/dev/smoke_api.py`)
- UI port / proxy target: set `INTELLI_UI_PORT` and `INTELLI_API_URL` when running the UI dev server

### 2) Configure environment

```bash
cp .env.example .env
```

Minimum recommended edits in `.env`:
- `DEBUG=true` (enables docs + demo bootstrap login)
- `OPENAI_API_KEY=...` (required for RAG indexing/asking)
- Optional: `CHAT_MODEL=...` (defaults to `gpt-4o-mini`)

### 3) Start infrastructure (Postgres + MinIO)

```bash
docker compose up -d postgres minio minio-init
```

Validate:
- Postgres ready:
  ```bash
  docker compose exec -T postgres pg_isready -U intelli
  ```
- MinIO healthy:
  ```bash
  curl -fsS http://localhost:9000/minio/health/live >/dev/null
  ```

### 4) Python environment + migrations

Create venv + install deps (first time only):
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run migrations:
```bash
alembic upgrade head
alembic current
```

Validate migration head:
```bash
alembic heads
```

If you previously migrated with the old revision ID `0001` (pre-normalization), your DB may be “out of sync”. Options:
- **Fastest for dev**: drop/recreate the DB volume (`docker compose down -v`) and rerun `alembic upgrade head`.
- If you need to preserve data: use `alembic stamp` carefully (only if you understand the state).

### 5) Start backend + verify health

```bash
uvicorn intelli.main:app --reload --port 8000
```

If port `8000` is already in use on your machine, pick a different one, e.g.:
```bash
INTELLI_API_PORT=8002 uvicorn intelli.main:app --reload --port 8002
```

Validate:
```bash
curl -fsS http://localhost:8000/health/ready
curl -fsS http://localhost:8000/health
```

### 6) API smoke test (subtrate + RAG)

In a second terminal (with venv activated):
```bash
python scripts/dev/smoke_api.py
```

This validates:
- Demo login (`/api/v1/auth/dev-bootstrap`) works (requires `DEBUG=true`)
- Pointer create
- Artifact upload (MinIO/S3 storage path)
- Manifest create + pointer advance
- RAG index + ask (runs only if `OPENAI_API_KEY` is set; add `--require-rag` to fail if missing)

### 7) UI install + typecheck/build

```bash
npm -C ui install
npm -C ui run typecheck
npm -C ui run build
```

Start UI:
```bash
npm -C ui run dev
```

If port `3000` is already in use, run:
```bash
INTELLI_UI_PORT=3011 INTELLI_API_URL=http://localhost:8002 npm -C ui run dev
```

Validate UI:
- Open `http://localhost:3000`
- Use “Demo Login”
- Create a notebook (`+` in Explorer), upload docs, index, ask

## Troubleshooting notes (common failures)

- `401/403` in UI: backend not running, or token not set; use “Demo Login” or ensure tenant/user exists.
- `/auth/dev-bootstrap` returns `404`: `DEBUG` is not enabled on the backend (`DEBUG=true` in `.env`).
- Upload fails: MinIO not running, bucket not created, or `.env` S3 settings mismatched.
- RAG fails during index/ask: `OPENAI_API_KEY` missing or invalid.
