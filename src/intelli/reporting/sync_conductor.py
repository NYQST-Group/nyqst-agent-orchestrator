"""Read-only validation for Conductor plan and GitHub issue alignment."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TASK_LINE_RE = re.compile(r"^(?P<indent>\s*)-\s+\[(?P<status>[ x~])\]\s+(?P<text>.+?)\s*$")
INLINE_ISSUE_RE = re.compile(r"#(?P<issue>\d+)\b")
COMMIT_SHA_SUFFIX_RE = re.compile(r"\s+[0-9a-f]{7,40}$")


@dataclass(frozen=True)
class TaskRecord:
    """Parsed task or sub-task line from a Conductor plan."""

    track_id: str
    plan_path: Path
    line_number: int
    status: str
    text: str
    inline_issue: int | None


@dataclass(frozen=True)
class TrackPolicy:
    """Validation policy for a given track."""

    enforce_mapping: bool
    reason: str | None
    task_mappings: dict[str, int]


def normalize_task_text(raw_text: str) -> str:
    """Normalize plan task text for stable sidecar mapping lookup."""
    text = COMMIT_SHA_SUFFIX_RE.sub("", raw_text.strip())
    text = INLINE_ISSUE_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_plan_tasks(root: Path) -> list[TaskRecord]:
    """Parse all Conductor plan task lines under the repository root."""
    tasks: list[TaskRecord] = []
    for plan_path in sorted((root / "conductor" / "tracks").glob("*/plan.md")):
        track_id = plan_path.parent.name
        for line_number, line in enumerate(plan_path.read_text(encoding="utf-8").splitlines(), start=1):
            match = TASK_LINE_RE.match(line)
            if not match:
                continue
            inline_match = INLINE_ISSUE_RE.search(match.group("text"))
            tasks.append(
                TaskRecord(
                    track_id=track_id,
                    plan_path=plan_path,
                    line_number=line_number,
                    status=match.group("status"),
                    text=normalize_task_text(match.group("text")),
                    inline_issue=int(inline_match.group("issue")) if inline_match else None,
                )
            )
    return tasks


def load_issue_map(map_path: Path) -> dict[str, Any]:
    """Load the task mapping policy file."""
    return json.loads(map_path.read_text(encoding="utf-8"))


def get_track_policy(track_id: str, issue_map: dict[str, Any]) -> TrackPolicy:
    """Resolve effective mapping policy for a track."""
    defaults = issue_map.get("defaults", {})
    track_config = issue_map.get("tracks", {}).get(track_id, {})
    mappings = {
        normalize_task_text(task_text): int(issue_number)
        for task_text, issue_number in track_config.get("task_mappings", {}).items()
    }
    return TrackPolicy(
        enforce_mapping=bool(track_config.get("enforce_mapping", defaults.get("enforce_mapping", False))),
        reason=track_config.get("reason"),
        task_mappings=mappings,
    )


def resolve_issue_number(task: TaskRecord, policy: TrackPolicy) -> int | None:
    """Resolve the issue number for a task from inline refs or sidecar mappings."""
    if task.inline_issue is not None:
        return task.inline_issue
    return policy.task_mappings.get(task.text)


def gh_issue_state(repo: str, issue_number: int) -> str:
    """Fetch the current GitHub issue state."""
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--repo",
                repo,
                "--json",
                "state",
                "--jq",
                ".state",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("GitHub CLI (gh) is required for conductor validation.") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown gh failure"
        raise RuntimeError(f"gh issue view #{issue_number} failed: {stderr}")

    state = result.stdout.strip().upper()
    if state not in {"OPEN", "CLOSED"}:
        raise RuntimeError(f"Unexpected issue state for #{issue_number}: {state or '<empty>'}")
    return state


def validate_tasks(root: Path, repo: str, map_path: Path) -> list[str]:
    """Validate plan task drift against GitHub issue state."""
    issue_map = load_issue_map(map_path)
    messages: list[str] = []

    for task in parse_plan_tasks(root):
        policy = get_track_policy(task.track_id, issue_map)
        issue_number = resolve_issue_number(task, policy)

        if policy.enforce_mapping and issue_number is None:
            messages.append(

                    f"{task.plan_path}:{task.line_number}: missing issue mapping for "
                    f"'{task.text}' in track '{task.track_id}'"

            )
            continue

        if issue_number is None:
            continue

        try:
            issue_state = gh_issue_state(repo, issue_number)
        except RuntimeError as exc:
            messages.append(f"{task.plan_path}:{task.line_number}: {exc}")
            continue

        if task.status == "x" and issue_state != "CLOSED":
            messages.append(

                    f"{task.plan_path}:{task.line_number}: task is complete but mapped issue "
                    f"#{issue_number} is {issue_state}"

            )
        elif task.status in {" ", "~"} and issue_state == "CLOSED":
            messages.append(

                    f"{task.plan_path}:{task.line_number}: task is not complete but mapped issue "
                    f"#{issue_number} is CLOSED"

            )

    return messages


def format_validation_report(root: Path, repo: str, map_path: Path) -> tuple[int, str]:
    """Return exit code and human-readable validation output."""
    messages = validate_tasks(root=root, repo=repo, map_path=map_path)
    if messages:
        joined = "\n".join(f"- {message}" for message in messages)
        return 1, f"Conductor validation failed:\n{joined}"
    return 0, "Conductor validation passed: no plan/GitHub drift detected."


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint used by sync-conductor.sh."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan")
    parser.add_argument(
        "--repo",
        default="NYQST-Group/NYQST-DocuIntelli-Build",
        help="GitHub repository in owner/name form",
    )
    parser.add_argument(
        "--map",
        dest="map_path",
        default="conductor/task_issue_map.json",
        help="Path to the conductor task issue map JSON file",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    map_path = (root / args.map_path).resolve() if not Path(args.map_path).is_absolute() else Path(args.map_path)
    exit_code, output = format_validation_report(root=root, repo=args.repo, map_path=map_path)
    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

