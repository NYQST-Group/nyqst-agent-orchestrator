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

is_port_free() {
  local port="$1"
  python - "$port" <<'PY'
import socket
import sys

port = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("127.0.0.1", port))
except OSError:
    sys.exit(1)
finally:
    s.close()
sys.exit(0)
PY
}

pick_port() {
  local label="$1"
  shift
  for port in "$@"; do
    if is_port_free "$port"; then
      echo "$port"
      return 0
    fi
  done
  die "No free port found for ${label} (tried: $*)"
}

pick_env_port() {
  local var_name="$1"
  local label="$2"
  shift 2
  local current="${!var_name:-}"
  if [[ -n "$current" ]]; then
    is_port_free "$current" || die "${label} port ${current} is already in use (set ${var_name})"
    export "$var_name=$current"
    return 0
  fi

  local chosen
  chosen="$(pick_port "$label" "$@")"
  export "$var_name=$chosen"
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

step "Pick infrastructure ports"
pick_env_port INTELLI_POSTGRES_PORT postgres 5433 15433 15434 15435
pick_env_port INTELLI_MINIO_API_PORT minio-api 9000 19000 19010 19020
pick_env_port INTELLI_MINIO_CONSOLE_PORT minio-console 9001 19001 19011 19021
pick_env_port INTELLI_OPENSEARCH_PORT opensearch 9200 19200 19210 19220

export DATABASE_URL="postgresql+asyncpg://intelli:intelli@localhost:${INTELLI_POSTGRES_PORT}/intelli"
export S3_ENDPOINT_URL="http://localhost:${INTELLI_MINIO_API_PORT}"
export OPENSEARCH_URL="http://localhost:${INTELLI_OPENSEARCH_PORT}"

echo "Using ports: postgres=${INTELLI_POSTGRES_PORT} minio=${INTELLI_MINIO_API_PORT}/${INTELLI_MINIO_CONSOLE_PORT} opensearch=${INTELLI_OPENSEARCH_PORT}"

step "Start infrastructure (postgres + minio + opensearch)"
docker compose up -d postgres minio minio-init opensearch

step "Wait for Postgres"
wait_for "postgres ready" "docker compose exec -T postgres pg_isready -U intelli" 60 1 \
  || die "Postgres did not become ready"

step "Wait for OpenSearch"
wait_for "opensearch health" "curl -fsS http://localhost:${INTELLI_OPENSEARCH_PORT} >/dev/null" 120 1 \
  || die "OpenSearch did not become healthy"

step "Wait for MinIO"
wait_for "minio health" "curl -fsS http://localhost:${INTELLI_MINIO_API_PORT}/minio/health/live" 60 1 \
  || die "MinIO did not become healthy"

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
if (( ${#RAG_FLAG[@]} > 0 )); then
  "$PY" scripts/dev/smoke_api.py "${RAG_FLAG[@]}" --base-url "http://localhost:${BACKEND_PORT}"
else
  "$PY" scripts/dev/smoke_api.py --base-url "http://localhost:${BACKEND_PORT}"
fi

step "UI sanity (typecheck + build)"
npm -C ui install
npm -C ui run typecheck
npm -C ui run build

step "Success"
echo "All validation steps passed."
echo "Next:"
echo "  - Start backend: source .venv/bin/activate && uvicorn intelli.main:app --reload --port 8000"
echo "  - Start UI:      npm -C ui run dev"
