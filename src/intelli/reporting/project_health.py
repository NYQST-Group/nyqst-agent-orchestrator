"""Repo-first project health reporting."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from intelli.reporting.sync_conductor import validate_tasks

WORKFLOW_FILE = Path(".github/workflows/backstage-schemas.yml")


@dataclass(frozen=True)
class HealthRisk:
    """A deterministic hygiene or delivery risk."""

    severity: str
    title: str
    detail: str
    source: str


@dataclass(frozen=True)
class HealthSnapshot:
    """Aggregated project health state."""

    generated_on: str
    repository: str
    total_issues: int
    open_issue_count: int
    milestone_count: int
    project_board_present: bool
    branch_protection_enabled: bool
    branch_protection_contexts: list[str]
    latest_workflows: dict[str, str]
    open_p0_titles: list[str]
    mock_contract_publisher: bool
    conductor_validation_errors: list[str]
    risks: list[HealthRisk]


def _run_json_command(command: list[str]) -> Any:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required command is not installed: {command[0]}") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown command failure"
        raise RuntimeError(f"Command failed ({' '.join(command)}): {stderr}")
    return json.loads(result.stdout)


def discover_repo() -> str:
    """Discover the current GitHub repository from gh."""
    result = _run_json_command(["gh", "repo", "view", "--json", "nameWithOwner"])
    return str(result["nameWithOwner"])


def list_issues(repo: str) -> list[dict[str, Any]]:
    """Fetch current GitHub issues."""
    return _run_json_command(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "300",
            "--json",
            "number,title,state,labels,milestone",
        ]
    )


def list_milestones(repo: str) -> list[dict[str, Any]]:
    """Fetch milestone metadata via the GitHub REST API."""
    return _run_json_command(["gh", "api", f"repos/{repo}/milestones?state=all&per_page=100"])


def get_branch_protection(repo: str) -> dict[str, Any]:
    """Fetch branch protection for main."""
    return _run_json_command(["gh", "api", f"repos/{repo}/branches/main/protection"])


def list_projects(owner: str) -> list[dict[str, Any]]:
    """Fetch GitHub Projects for the repository owner."""
    payload = _run_json_command(["gh", "project", "list", "--owner", owner, "--format", "json"])
    if isinstance(payload, dict):
        projects = payload.get("projects", [])
        if isinstance(projects, list):
            return projects
    if isinstance(payload, list):
        return payload
    raise RuntimeError("Unexpected GitHub Projects payload shape.")


def list_workflow_runs(repo: str) -> list[dict[str, Any]]:
    """Fetch recent GitHub Actions runs."""
    return _run_json_command(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--limit",
            "20",
            "--json",
            "workflowName,status,conclusion,createdAt,headBranch,event",
        ]
    )


def has_mock_contract_publisher(root: Path) -> bool:
    """Detect whether the contract publisher workflow is still explicitly mocked."""
    workflow_path = root / WORKFLOW_FILE
    if not workflow_path.exists():
        return False
    return "currently a mock" in workflow_path.read_text(encoding="utf-8").lower()


def latest_workflow_statuses(workflow_runs: list[dict[str, Any]]) -> dict[str, str]:
    """Collapse recent workflow runs to the latest conclusion per workflow."""
    latest: dict[str, tuple[str, str]] = {}
    for workflow_run in workflow_runs:
        workflow_name = workflow_run.get("workflowName") or "Unnamed workflow"
        created_at = workflow_run.get("createdAt") or ""
        conclusion = workflow_run.get("conclusion") or workflow_run.get("status") or "unknown"
        current = latest.get(workflow_name)
        if current is None or created_at > current[0]:
            latest[workflow_name] = (created_at, conclusion)
    return {name: conclusion for name, (_created_at, conclusion) in sorted(latest.items())}


def evaluate_risks(
    *,
    conductor_validation_errors: list[str],
    branch_protection: dict[str, Any],
    workflow_statuses: dict[str, str],
    open_p0_titles: list[str],
    mock_contract_publisher: bool,
) -> list[HealthRisk]:
    """Apply deterministic hygiene rules."""
    risks: list[HealthRisk] = []

    required_checks = branch_protection.get("required_status_checks", {})
    contexts = required_checks.get("contexts", []) if isinstance(required_checks, dict) else []
    if not contexts:
        risks.append(
            HealthRisk(
                severity="critical",
                title="Main branch protection missing",
                detail="The main branch does not expose required status checks.",
                source="GitHub branch protection",
            )
        )

    if conductor_validation_errors:
        risks.append(
            HealthRisk(
                severity="high",
                title="Conductor plan / issue drift detected",
                detail=f"{len(conductor_validation_errors)} validation issue(s) need correction.",
                source="sync-conductor validation",
            )
        )

    for workflow_name, conclusion in workflow_statuses.items():
        if conclusion not in {"success", "skipped"}:
            risks.append(
                HealthRisk(
                    severity="high",
                    title=f"Workflow not green: {workflow_name}",
                    detail=f"The latest recorded conclusion is '{conclusion}'.",
                    source="GitHub Actions",
                )
            )

    if open_p0_titles:
        risks.append(
            HealthRisk(
                severity="high",
                title="P0 stabilization work remains open",
                detail="Open P0 items: " + "; ".join(open_p0_titles),
                source="GitHub issues",
            )
        )

    if mock_contract_publisher:
        risks.append(
            HealthRisk(
                severity="medium",
                title="Contract publisher is still mocked",
                detail="The backstage schema publishing workflow still exits with a mock/incomplete implementation.",
                source="Workflow file",
            )
        )

    return risks


def build_snapshot(
    *,
    root: Path,
    repo: str,
    report_date: date,
    owner: str | None = None,
) -> HealthSnapshot:
    """Collect all reporting inputs and compute the current health snapshot."""
    owner_name = owner or repo.split("/", 1)[0]
    conductor_validation_errors = validate_tasks(
        root=root,
        repo=repo,
        map_path=root / "conductor" / "task_issue_map.json",
    )
    issues = list_issues(repo)
    milestones = list_milestones(repo)
    branch_protection = get_branch_protection(repo)
    projects = list_projects(owner_name)
    workflow_runs = list_workflow_runs(repo)
    workflow_statuses = latest_workflow_statuses(workflow_runs)
    open_p0_titles = sorted(issue["title"] for issue in issues if str(issue.get("title", "")).startswith("[P0-"))
    mock_contract_publisher = has_mock_contract_publisher(root)
    risks = evaluate_risks(
        conductor_validation_errors=conductor_validation_errors,
        branch_protection=branch_protection,
        workflow_statuses=workflow_statuses,
        open_p0_titles=open_p0_titles,
        mock_contract_publisher=mock_contract_publisher,
    )
    project_names = {project.get("title", "") for project in projects}

    return HealthSnapshot(
        generated_on=report_date.isoformat(),
        repository=repo,
        total_issues=len(issues),
        open_issue_count=sum(1 for issue in issues if issue.get("state") == "OPEN"),
        milestone_count=len(milestones),
        project_board_present="Project Meta-Reporting & Health Tracking" in project_names
        or "Superagent Parity" in project_names,
        branch_protection_enabled=bool(branch_protection),
        branch_protection_contexts=sorted(
            (branch_protection.get("required_status_checks") or {}).get("contexts", [])
        ),
        latest_workflows=workflow_statuses,
        open_p0_titles=open_p0_titles,
        mock_contract_publisher=mock_contract_publisher,
        conductor_validation_errors=conductor_validation_errors,
        risks=risks,
    )


def render_markdown_report(snapshot: HealthSnapshot) -> str:
    """Render the dated Markdown health report."""
    workflow_lines = "\n".join(
        f"- `{name}`: `{conclusion}`" for name, conclusion in snapshot.latest_workflows.items()
    ) or "- No workflow data captured."
    validation_lines = "\n".join(
        f"- {message}" for message in snapshot.conductor_validation_errors
    ) or "- No conductor drift detected."
    risk_lines = "\n".join(
        f"- `{risk.severity.upper()}` {risk.title}: {risk.detail} ({risk.source})"
        for risk in snapshot.risks
    ) or "- No active risks."
    p0_lines = "\n".join(f"- {title}" for title in snapshot.open_p0_titles) or "- No open P0 issues."

    return "\n".join(
        [
            f"# Project Health Report - {snapshot.generated_on}",
            "",
            f"- Repository: `{snapshot.repository}`",
            f"- Total issues: `{snapshot.total_issues}`",
            f"- Open issues: `{snapshot.open_issue_count}`",
            f"- Milestones: `{snapshot.milestone_count}`",
            f"- Branch protection enabled: `{snapshot.branch_protection_enabled}`",
            f"- Required status checks: `{', '.join(snapshot.branch_protection_contexts) or 'none'}`",
            f"- Reporting project board present: `{snapshot.project_board_present}`",
            f"- Mock contract publisher present: `{snapshot.mock_contract_publisher}`",
            "",
            "## Latest Workflow Statuses",
            workflow_lines,
            "",
            "## Conductor Validation",
            validation_lines,
            "",
            "## Open P0 Issues",
            p0_lines,
            "",
            "## Active Risks",
            risk_lines,
            "",
            "## Notes",
            "- Reporting remains repo-first; GitHub Project automation is intentionally deferred.",
            "- GitHub issue closure remains governed by PR merge semantics, not local plan checkbox mutation.",
        ]
    ) + "\n"


def render_json_report(snapshot: HealthSnapshot) -> str:
    """Render the JSON health report."""
    payload = asdict(snapshot)
    payload["risks"] = [asdict(risk) for risk in snapshot.risks]
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_risk_register(snapshot: HealthSnapshot) -> str:
    """Render the repo-local risk register from the current snapshot."""
    risk_lines = "\n".join(
        f"- `{risk.severity.upper()}` {risk.title}: {risk.detail} ({risk.source})"
        for risk in snapshot.risks
    ) or "- No active risks."

    return "\n".join(
        [
            "# Risk Register",
            "",
            f"- Last generated: `{snapshot.generated_on}T00:00:00Z`",
            f"- Repository: `{snapshot.repository}`",
            f"- Report date: `{snapshot.generated_on}`",
            "",
            "## Current Risks",
            risk_lines,
            "",
            "## Reporting Policy",
            "- Repo-first reporting is the current source of truth.",
            "- GitHub Project mutation is deferred until a dedicated board is provisioned.",
            "- Conductor drift is detected by validation, not resolved by automatic issue closure.",
        ]
    ) + "\n"
