#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/.codex"
target_dir="${1:-$repo_root/.codex}"

if [[ ! -d "$source_dir" ]]; then
  echo "Missing source Codex config at $source_dir" >&2
  exit 1
fi

mkdir -p "$target_dir"
rsync -a --delete "$source_dir/" "$target_dir/"

cat <<EOF
Synced Codex Team Config from:
  $source_dir
to:
  $target_dir
EOF
