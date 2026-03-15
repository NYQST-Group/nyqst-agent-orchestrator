#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

[[ -x .venv/bin/python ]] || {
  echo "Missing .venv. Run ./tools/bootstrap_worktree.sh first." >&2
  exit 1
}

.venv/bin/python -m ruff check src/ tests/
.venv/bin/python -m ruff format --check src/ tests/
.venv/bin/python -m pytest -m unit -q
npm -C ui run lint
npm -C ui run typecheck
npm -C ui run test
