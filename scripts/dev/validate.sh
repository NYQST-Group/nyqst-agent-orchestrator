#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

step() {
  echo
  echo "==> $*"
}

die() {
  echo
  echo "ERROR: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

wait_for() {
  local desc="$1"
  local cmd="$2"
  local attempts="${3:-30}"
  local sleep_s="${4:-1}"

  for ((i=1; i<=attempts; i++)); do
    if eval "$cmd" >/dev/null 2>&1; then
      echo "OK: $desc"
      return 0
    fi
    sleep "$sleep_s"
  done

echo "FAILED: $desc"
echo "Command: $cmd"
return 1
}

step "Prereqs"
require_cmd docker
require_cmd python3
require_cmd curl
require_cmd node
require_cmd npm
docker compose version >/dev/null 2>&1 || die "docker compose plugin not available"

step "Git status"
if command -v git >/dev/null 2>&1; then
  git status -sb || true
else
  echo "WARN: git not found; skipping"
fi

step "Ensure .env"
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example (edit OPENAI_API_KEY for full RAG smoke test)"
fi

step "Start infrastructure (postgres + minio + opensearch)"
docker compose up -d postgres minio minio-init opensearch

step "Wait for Postgres"
wait_for "postgres ready" "docker compose exec -T postgres pg_isready -U intelli" 60 1 \
  || die "Postgres did not become ready"

step "Wait for MinIO"
wait_for "minio health" "curl -fsS http://localhost:9000/minio/health/live" 60 1 \
  || die "MinIO did not become healthy"

step "Wait for OpenSearch"
wait_for "opensearch health" "curl -fsS http://localhost:9200 >/dev/null" 120 1 \
  || die "OpenSearch did not become healthy"

step "Python venv + deps"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

PY="$ROOT_DIR/.venv/bin/python"
PIP="$ROOT_DIR/.venv/bin/pip"

"$PY" -m pip --version >/dev/null

if ! "$PY" -c "import intelli" >/dev/null 2>&1; then
  "$PIP" install -e ".[dev]"
fi
"$PY" -c "import email_validator" >/dev/null 2>&1 || "$PIP" install "email-validator>=2.0.0"

"$PY" - <<'PY'
import fastapi  # noqa: F401
import sqlalchemy  # noqa: F401
import asyncpg  # noqa: F401
import docling  # noqa: F401
import openai  # noqa: F401
import email_validator  # noqa: F401
from pgvector.sqlalchemy import Vector  # noqa: F401
print("OK: python deps import")
PY

step "Migrations"
"$PY" -m alembic upgrade head
"$PY" -m alembic heads
"$PY" -m alembic current

step "Backend sanity"
"$PY" -m compileall -q src/intelli

step "Start backend (temporary) + health check"
BACKEND_PORT="${INTELLI_API_PORT:-8000}"
"$PY" -m uvicorn intelli.main:app --port "$BACKEND_PORT" --log-level warning &
BACKEND_PID=$!
cleanup() {
  if kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

wait_for "backend /health/ready" "curl -fsS http://localhost:${BACKEND_PORT}/health/ready" 60 1 \
  || die "Backend did not become ready"

step "API smoke test"
RAG_FLAG=()
if [[ "${INTELLI_REQUIRE_RAG:-0}" != "0" ]]; then
  RAG_FLAG+=(--require-rag)
fi
"$PY" scripts/dev/smoke_api.py "${RAG_FLAG[@]}" --base-url "http://localhost:${BACKEND_PORT}"

step "UI sanity (typecheck + build)"
npm -C ui install
npm -C ui run typecheck
npm -C ui run build

step "Success"
echo "All validation steps passed."
echo "Next:"
echo "  - Start backend: source .venv/bin/activate && uvicorn intelli.main:app --reload --port 8000"
echo "  - Start UI:      npm -C ui run dev"
