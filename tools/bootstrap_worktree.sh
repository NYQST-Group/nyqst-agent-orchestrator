#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

PYTHON_BIN="${PYTHON_BIN:-$(command -v python || command -v python3)}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

echo "==> Repo worktree bootstrap"
require_cmd git
require_cmd npm
require_cmd "$PYTHON_BIN"

if [[ ! -d .venv ]]; then
  echo "Creating .venv"
  "$PYTHON_BIN" -m venv .venv
fi

echo "Installing Python dependencies"
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/pip install -e ".[dev]"

echo "Installing UI dependencies"
npm -C ui install

echo "Worktree bootstrap complete."
