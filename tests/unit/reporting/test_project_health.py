"""Fixture-backed tests for repo-first project health reporting."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

import intelli.reporting.project_health as project_health

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "reporting"


def _load_json(name: str) -> object:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _load_text(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _build_fixture_snapshot(monkeypatch: pytest.MonkeyPatch) -> project_health.HealthSnapshot:
    monkeypatch.setattr(project_health, "validate_tasks", lambda **_: _load_json("validation_errors.json"))
    monkeypatch.setattr(project_health, "list_issues", lambda repo: _load_json("issues.json"))
    monkeypatch.setattr(project_health, "list_milestones", lambda repo: _load_json("milestones.json"))
    monkeypatch.setattr(project_health, "get_branch_protection", lambda repo: _load_json("branch_protection.json"))
    monkeypatch.setattr(project_health, "list_projects", lambda owner: _load_json("projects.json"))
    monkeypatch.setattr(project_health, "list_workflow_runs", lambda repo: _load_json("workflow_runs.json"))
    monkeypatch.setattr(project_health, "has_mock_contract_publisher", lambda root: True)
    return project_health.build_snapshot(
        root=Path("/tmp/repo"),
        repo="NYQST-Group/NYQST-DocuIntelli-Build",
        report_date=date(2026, 3, 11),
    )


class TestBuildSnapshot:
    def test_aggregates_fixture_data_without_live_github_calls(self, monkeypatch: pytest.MonkeyPatch):
        snapshot = _build_fixture_snapshot(monkeypatch)

        assert snapshot.total_issues == 4
        assert snapshot.open_issue_count == 3
        assert snapshot.milestone_count == 2
        assert snapshot.project_board_present is False
        assert snapshot.branch_protection_enabled is True
        assert snapshot.branch_protection_contexts == ["Backend Tests", "Lint"]
        assert snapshot.latest_workflows == {
            "Backend Tests": "success",
            "External Schema Publisher": "failure",
            "Lint": "success",
        }
        assert snapshot.open_p0_titles == ["[P0-004] Add tenant_id to core run tables"]
        assert snapshot.mock_contract_publisher is True
        assert len(snapshot.risks) == 4


class TestEvaluateRisks:
    def test_flags_missing_branch_protection(self):
        risks = project_health.evaluate_risks(
            conductor_validation_errors=[],
            branch_protection={},
            workflow_statuses={},
            open_p0_titles=[],
            mock_contract_publisher=False,
        )

        assert any(risk.title == "Main branch protection missing" for risk in risks)


class TestRenderers:
    def test_markdown_report_matches_golden_output(self, monkeypatch: pytest.MonkeyPatch):
        snapshot = _build_fixture_snapshot(monkeypatch)
        assert project_health.render_markdown_report(snapshot) == _load_text("expected_report.md")

    def test_json_report_matches_golden_output(self, monkeypatch: pytest.MonkeyPatch):
        snapshot = _build_fixture_snapshot(monkeypatch)
        assert project_health.render_json_report(snapshot) == _load_text("expected_report.json")

    def test_risk_register_matches_golden_output(self, monkeypatch: pytest.MonkeyPatch):
        snapshot = _build_fixture_snapshot(monkeypatch)
        assert project_health.render_risk_register(snapshot) == _load_text("expected_risk_register.md")
