#!/usr/bin/env python3
"""Generate repo-first project health outputs and refresh the risk register."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> int:
    from intelli.reporting.project_health import (
        build_snapshot,
        discover_repo,
        render_json_report,
        render_markdown_report,
        render_risk_register,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--repo", default=None, help="GitHub repository in owner/name form")
    parser.add_argument("--date", dest="report_date", default=None, help="Override report date (YYYY-MM-DD)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    repo = args.repo or discover_repo()
    report_date = date.fromisoformat(args.report_date) if args.report_date else date.today()

    snapshot = build_snapshot(root=root, repo=repo, report_date=report_date)

    reports_dir = root / "reports" / "project_health"
    reports_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = reports_dir / f"{report_date.isoformat()}.md"
    json_path = reports_dir / f"{report_date.isoformat()}.json"

    markdown_path.write_text(render_markdown_report(snapshot), encoding="utf-8")
    json_path.write_text(render_json_report(snapshot), encoding="utf-8")
    (root / "RISK_REGISTER.md").write_text(render_risk_register(snapshot), encoding="utf-8")

    print(f"Wrote {markdown_path}")
    print(f"Wrote {json_path}")
    print(f"Updated {root / 'RISK_REGISTER.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
