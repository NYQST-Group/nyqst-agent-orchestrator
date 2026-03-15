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
