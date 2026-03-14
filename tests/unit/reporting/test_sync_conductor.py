"""Subprocess tests for the read-only Conductor validator wrapper."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNC_SCRIPT = REPO_ROOT / "sync-conductor.sh"


def _write_fake_gh(bin_dir: Path) -> None:
    gh_path = bin_dir / "gh"
    gh_path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" != "issue" ] || [ "${2:-}" != "view" ]; then
    echo "unsupported gh invocation: $*" >&2
    exit 1
fi

issue_number="${3:-}"
case "${GH_CASE:-}" in
    open)
        echo "OPEN"
        ;;
    closed)
        echo "CLOSED"
        ;;
    fail)
        echo "simulated gh failure for #${issue_number}" >&2
        exit 1
        ;;
    *)
        echo "unsupported GH_CASE: ${GH_CASE:-<unset>}" >&2
        exit 1
        ;;
esac
""",
        encoding="utf-8",
    )
    gh_path.chmod(0o755)


def _write_temp_repo(tmp_path: Path, *, plan_text: str, issue_map: dict[str, object]) -> Path:
    repo_root = tmp_path / "repo"
    plan_dir = repo_root / "conductor" / "tracks" / "example_track"
    plan_dir.mkdir(parents=True)
    (plan_dir / "plan.md").write_text(plan_text, encoding="utf-8")
    (repo_root / "conductor" / "task_issue_map.json").write_text(
        json.dumps(issue_map, indent=2),
        encoding="utf-8",
    )
    return repo_root


def _run_sync(repo_root: Path, bin_dir: Path, gh_case: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["GH_CASE"] = gh_case
    return subprocess.run(
        [
            str(SYNC_SCRIPT),
            "--root",
            str(repo_root),
            "--repo",
            "example/repo",
            "--map",
            str(repo_root / "conductor" / "task_issue_map.json"),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


class TestSyncConductorWrapper:
    def test_fails_when_required_issue_mapping_is_missing(self, tmp_path: Path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _write_fake_gh(bin_dir)
        repo_root = _write_temp_repo(
            tmp_path,
            plan_text="# Plan\n- [x] Task: Correct historical metadata\n",
            issue_map={
                "defaults": {"enforce_mapping": False},
                "tracks": {"example_track": {"enforce_mapping": True, "task_mappings": {}}},
            },
        )

        result = _run_sync(repo_root, bin_dir, gh_case="closed")

        assert result.returncode == 1
        assert "missing issue mapping" in result.stdout

    def test_fails_when_gh_issue_lookup_errors(self, tmp_path: Path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _write_fake_gh(bin_dir)
        repo_root = _write_temp_repo(
            tmp_path,
            plan_text="# Plan\n- [x] Task: Correct historical metadata #101\n",
            issue_map={"defaults": {"enforce_mapping": False}, "tracks": {}},
        )

        result = _run_sync(repo_root, bin_dir, gh_case="fail")

        assert result.returncode == 1
        assert "gh issue view #101 failed" in result.stdout

    def test_fails_when_completed_task_maps_to_open_issue(self, tmp_path: Path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _write_fake_gh(bin_dir)
        repo_root = _write_temp_repo(
            tmp_path,
            plan_text="# Plan\n- [x] Task: Correct historical metadata #101\n",
            issue_map={"defaults": {"enforce_mapping": False}, "tracks": {}},
        )

        result = _run_sync(repo_root, bin_dir, gh_case="open")

        assert result.returncode == 1
        assert "task is complete but mapped issue #101 is OPEN" in result.stdout

    def test_passes_when_completed_task_maps_to_closed_issue(self, tmp_path: Path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _write_fake_gh(bin_dir)
        repo_root = _write_temp_repo(
            tmp_path,
            plan_text="# Plan\n- [x] Task: Correct historical metadata #101\n",
            issue_map={"defaults": {"enforce_mapping": False}, "tracks": {}},
        )

        result = _run_sync(repo_root, bin_dir, gh_case="closed")

        assert result.returncode == 0
        assert "Conductor validation passed" in result.stdout
