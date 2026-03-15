#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

AO_CONFIG_PATH="$repo_root/agent-orchestrator.yaml" ao doctor "$@"
