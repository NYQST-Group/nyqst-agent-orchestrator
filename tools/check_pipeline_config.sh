#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

required_files=(
  "agent-orchestrator.yaml"
  "ao-agent-rules.md"
  ".codex/config.toml"
  ".codex/managed_config.toml"
  ".codex/requirements.toml"
  ".codex/ao-worker-rules.md"
  ".github/pull_request_template.md"
  ".github/ISSUE_TEMPLATE/config.yml"
  ".github/ISSUE_TEMPLATE/01-packet.yml"
  ".github/ISSUE_TEMPLATE/02-experiment.yml"
  ".github/ISSUE_TEMPLATE/03-bug.yml"
  "docs/runbooks/ao-codex-pipeline.md"
  "tools/bootstrap_worktree.sh"
  "tools/run_repo_checks.sh"
)

for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || {
    echo "Missing required file: $file" >&2
    exit 1
  }
done

PYTHON_BIN="${PYTHON_BIN:-$(command -v python || command -v python3)}"

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - local macOS fallback
    import tomli as tomllib

for rel in [
    ".codex/config.toml",
    ".codex/managed_config.toml",
    ".codex/requirements.toml",
]:
    with Path(rel).open("rb") as handle:
        tomllib.load(handle)
PY

ruby -e 'require "yaml"; ARGV.each { |path| YAML.load_file(path) }' \
  agent-orchestrator.yaml \
  .github/ISSUE_TEMPLATE/config.yml \
  .github/ISSUE_TEMPLATE/01-packet.yml \
  .github/ISSUE_TEMPLATE/02-experiment.yml \
  .github/ISSUE_TEMPLATE/03-bug.yml

ruby -e '
require "yaml"
config = YAML.load_file("agent-orchestrator.yaml")
project = config.fetch("projects").fetch("nyqst")
scm = project["scm"]
abort("agent-orchestrator.yaml must declare projects.nyqst.scm.plugin") unless scm.is_a?(Hash) && scm["plugin"].to_s != ""
' 

grep -q "AO Session" .github/pull_request_template.md
grep -q "Task Brief" .github/pull_request_template.md
grep -q "Verification" .github/pull_request_template.md

bash -n tools/sync_codex_team_config.sh
bash -n tools/ao_doctor_local.sh
bash -n tools/bootstrap_ao_codex.sh
bash -n tools/bootstrap_worktree.sh
bash -n tools/run_repo_checks.sh
bash -n scripts/dev/run.sh
bash -n scripts/dev/validate.sh
bash -n scripts/smoke-test.sh
