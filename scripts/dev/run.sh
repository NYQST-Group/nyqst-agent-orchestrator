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

postgres_ready() {
  local db_url="${DATABASE_URL:-postgresql+asyncpg://intelli:intelli@localhost:${INTELLI_POSTGRES_PORT:-5433}/intelli}"
  "$PY" - "$db_url" <<'PY'
import asyncio
import sys

import asyncpg

dsn = sys.argv[1].replace("postgresql+asyncpg://", "postgresql://", 1)

async def main() -> None:
    conn = await asyncpg.connect(dsn, timeout=1)
    await conn.close()

asyncio.run(main())
PY
}

ensure_service() {
  local label="$1"
  local check_cmd="$2"
  shift 2

  if eval "$check_cmd" >/dev/null 2>&1; then
    echo "Using existing ${label}"
    return 0
  fi

  docker compose up -d "$@"
}

is_port_free() {
  local port="$1"
  python3 - "$port" <<'PY'
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

step "Prereqs"
require_cmd docker
require_cmd python3
require_cmd curl
require_cmd node
require_cmd npm
docker compose version >/dev/null 2>&1 || die "docker compose plugin not available"

step "Ensure .env"
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

step "Python venv + deps"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

PY="$ROOT_DIR/.venv/bin/python"
PIP="$ROOT_DIR/.venv/bin/pip"

if ! "$PY" -m pip --version >/dev/null 2>&1; then
  "$PY" -m ensurepip --upgrade
fi

if ! "$PY" -c "import intelli" >/dev/null 2>&1; then
  "$PIP" install -e ".[dev]"
fi
"$PY" -c "import email_validator" >/dev/null 2>&1 || "$PIP" install "email-validator>=2.0.0"

MINIO_HEALTH_URL="${S3_ENDPOINT_URL:-http://localhost:9000}/minio/health/live"
OPENSEARCH_BASE_URL="${OPENSEARCH_URL:-http://localhost:9200}"

step "Start infrastructure (postgres + minio + opensearch)"
ensure_service "Postgres" "postgres_ready" postgres
ensure_service "MinIO" "curl -fsS '${MINIO_HEALTH_URL}'" minio minio-init
ensure_service "OpenSearch" "curl -fsS '${OPENSEARCH_BASE_URL}' >/dev/null" opensearch

step "Migrations"
"$PY" -m alembic upgrade head

step "Start backend"
if [[ -n "${INTELLI_API_PORT:-}" ]]; then
  BACKEND_PORT="${INTELLI_API_PORT}"
  is_port_free "$BACKEND_PORT" || die "Backend port ${BACKEND_PORT} is already in use (set INTELLI_API_PORT)"
else
  BACKEND_PORT="$(pick_port backend 8000 8001 8002 8003 8004 8005)"
fi
export INTELLI_API_PORT="$BACKEND_PORT"

BACKEND_ARGS=(--port "$BACKEND_PORT" --log-level info)
if [[ "${INTELLI_BACKEND_RELOAD:-0}" != "0" ]]; then
  BACKEND_ARGS+=(--reload)
fi

"$PY" -m uvicorn intelli.main:app "${BACKEND_ARGS[@]}" &
BACKEND_PID=$!

cleanup() {
  if kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

for _ in {1..60}; do
  if curl -fsS "http://localhost:${BACKEND_PORT}/health/ready" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl -fsS "http://localhost:${BACKEND_PORT}/health/ready" >/dev/null 2>&1 \
  || die "Backend did not become ready on port ${BACKEND_PORT}"

step "UI deps"
if [[ ! -d ui/node_modules ]]; then
  npm -C ui install
fi

step "Start UI"
if [[ -n "${INTELLI_UI_PORT:-}" ]]; then
  UI_PORT="${INTELLI_UI_PORT}"
  is_port_free "$UI_PORT" || die "UI port ${UI_PORT} is already in use (set INTELLI_UI_PORT)"
else
  UI_PORT="$(pick_port ui 3000 3001 3002 3010 3011 3012 5173 5174)"
fi

export INTELLI_UI_PORT="$UI_PORT"
export INTELLI_API_URL="${INTELLI_API_URL:-http://localhost:${BACKEND_PORT}}"

echo
echo "Backend: http://localhost:${BACKEND_PORT} (docs: /docs)"
echo "UI:      http://localhost:${UI_PORT}"
echo
echo "Tip: set OPENAI_API_KEY in .env to enable RAG index/ask."

npm -C ui run dev
