# Specification: Project Meta-Reporting & Health Tracking

## Overview
This track implements an automated meta-reporting framework that runs at the end of every Conductor phase. The objective is to calculate and track project progress, enforce project implementation hygiene, and surface meta-issues (flaws in the execution process, not just code bugs). 

## Functional Requirements
1. **Multi-Source Aggregation**:
   - The reporting script must calculate progress by extracting state from three sources: Conductor `plan.md` sub-task checkboxes, GitHub Issue statuses via the `gh` CLI, and CI/CD metrics (test coverage, build success rates).
2. **GitHub Project View Integration**:
   - Instead of a flat markdown file, the reporting tool must push updates into a structured GitHub Project board.
   - We must design and provision a GitHub Project View with custom fields (e.g., "Health", "Blocked Reason", "Coverage %") to visualize this data dynamically.
3. **Meta-Issue Management**:
   - The system must evaluate the aggregated data against project standards. If execution hygiene fails (e.g., coverage drops below 80%, issues are merged without linked Conductor tasks, tests are skipped), the system must:
     - Automatically create a new GitHub Issue labeled `meta-risk` or `process-debt`.
     - Update a central, committed `RISK_REGISTER.md` file locally in the repository.
4. **Trigger Mechanism**:
   - The report generation is triggered at the end of every Conductor Phase. The AI agent executing the phase will invoke the reporting script as a mandatory step in the Phase Completion Protocol.

## Non-Functional Requirements
- Uses the GitHub API / `gh` CLI for secure operations.
- Must execute deterministically and idempotently.

## Out of Scope
- Code linting (handled by CI/CD separately; this track only *reports* on CI/CD success).