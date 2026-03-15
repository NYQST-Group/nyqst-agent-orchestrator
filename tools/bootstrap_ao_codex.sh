#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

CODEX_HOME_ROOT="${AO_CODEX_HOME:-$HOME/.codex}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

echo "==> Prerequisites"
require_cmd ao
require_cmd codex
require_cmd gh
require_cmd git
require_cmd tmux
require_cmd rsync

echo "==> GitHub auth"
gh auth status >/dev/null

echo "==> Codex auth"
codex_status="$(codex login status 2>&1)"
printf '%s\n' "$codex_status"
grep -q "Logged in using ChatGPT" <<<"$codex_status" || {
  echo "Codex must be logged in with ChatGPT OAuth before bootstrap." >&2
  exit 1
}

echo "==> AO doctor"
AO_CONFIG_PATH="$repo_root/agent-orchestrator.yaml" ao doctor

echo "==> Local repo bootstrap"
"$repo_root/tools/bootstrap_worktree.sh"

echo "==> Smoke-test orchestrator lane"
CODEX_HOME="$CODEX_HOME_ROOT" codex -C "$repo_root" exec \
  --profile nyqst_ao_orchestrator \
  --model gpt-5.4 \
  "Respond with exactly the word ready."

echo "==> Smoke-test worker lane"
CODEX_HOME="$CODEX_HOME_ROOT" codex -C "$repo_root" exec \
  --profile nyqst_ao_worker \
  --model gpt-5.4 \
  -c service_tier=fast \
  "Respond with exactly the word ready."

echo "==> Complete"
echo "Codex home: $CODEX_HOME_ROOT"
