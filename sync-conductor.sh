#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required for conductor validation." >&2
    exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "Error: GitHub CLI (gh) is required for conductor validation." >&2
    exit 1
fi

PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
  python3 -m intelli.reporting.sync_conductor \
    --root "$ROOT_DIR" \
    --map "conductor/task_issue_map.json" \
    "$@"
