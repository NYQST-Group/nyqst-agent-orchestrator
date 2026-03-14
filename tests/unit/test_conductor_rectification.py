"""Consistency checks for the tracks 1-4 rectification artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
RECTIFICATION_TRACK_ID = "meta_tracks_rectification_20260311"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_override_target_ids(text: str) -> set[str]:
    ids = set(re.findall(r"\b(?:BL|P0|OBS|STUDIO)-\d{3}\b|\bEPIC-P0\b|\bSTORY-PROD-\d{3}\b", text))
    if "STUDIO-001" in text and "STUDIO-005" in text and "through" in text:
        ids.update({f"STUDIO-{number:03d}" for number in range(1, 6)})
    return ids


def test_historical_track_metadata_has_been_rectified():
    expectations = {
        "meta_f2b_bootstrap_20260308": "partial",
        "project_reporting_20260308": "superseded",
        "legacy_issue_sanitization_20260308": "partial",
        "meta_build_process_analysis_20260308": "partial",
    }

    for track_id, expected_status in expectations.items():
        metadata = _load_json(REPO_ROOT / "conductor" / "tracks" / track_id / "metadata.json")
        assert metadata["status"] == expected_status
        assert metadata["status"] != "new"
        assert metadata["rectified_by_track_id"] == RECTIFICATION_TRACK_ID


def test_rectified_plan_annotations_match_corrected_statuses():
    expectations = {
        "meta_f2b_bootstrap_20260308": "[~]",
        "project_reporting_20260308": "Superseded on March 11, 2026",
        "legacy_issue_sanitization_20260308": "[~]",
        "meta_build_process_analysis_20260308": "[~]",
    }

    for track_id, marker in expectations.items():
        plan_text = (REPO_ROOT / "conductor" / "tracks" / track_id / "plan.md").read_text(encoding="utf-8")
        assert "## Rectification Note" in plan_text
        assert marker in plan_text


def test_rectification_track_is_complete():
    metadata = _load_json(REPO_ROOT / "conductor" / "tracks" / RECTIFICATION_TRACK_ID / "metadata.json")
    plan_text = (REPO_ROOT / "conductor" / "tracks" / RECTIFICATION_TRACK_ID / "plan.md").read_text(
        encoding="utf-8"
    )

    assert metadata["status"] == "completed"
    assert "[ ]" not in plan_text
    assert "[~]" not in plan_text


def test_sanitization_manifest_covers_all_override_targets():
    override_targets = _extract_override_target_ids((REPO_ROOT / "V4_OVERRIDE_TARGETS.md").read_text(encoding="utf-8"))
    manifest = _load_json(REPO_ROOT / "staging_issues" / "SANITIZATION_MANIFEST.json")
    manifest_ids = {entry["id"] for entry in manifest["entries"]}

    assert override_targets.issubset(manifest_ids)
