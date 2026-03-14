# Specification: Project Meta-Reporting & Health Tracking

## Rectification Note
This specification remains useful as historical intent, but its GitHub Project mutation requirements were not implemented and are now deferred. As of March 11, 2026, the supported deliverable is a repo-first reporting flow that writes dated Markdown/JSON reports plus `RISK_REGISTER.md` from deterministic GitHub and Conductor inputs.

## Overview
This track implements an automated meta-reporting framework that runs at the end of every Conductor phase. The objective is to calculate and track project progress, enforce project implementation hygiene, and surface meta-issues (flaws in the execution process, not just code bugs). 

## Functional Requirements
1. **Multi-Source Aggregation**:
   - The reporting script must calculate progress by extracting state from three sources: Conductor `plan.md` sub-task checkboxes, GitHub Issue statuses via the `gh` CLI, and CI/CD metrics (test coverage, build success rates).
2. **GitHub Project View Integration**:
   - This is deferred to a later phase. No reporting board is assumed to exist in the current repository state.
   - Current reporting outputs are committed files under `reports/project_health/` plus `RISK_REGISTER.md`.
3. **Meta-Issue Management**:
   - The system must evaluate the aggregated data against project standards. If execution hygiene fails (e.g., coverage drops below 80%, issues are merged without linked Conductor tasks, tests are skipped), the system must:
     - Update a central, committed `RISK_REGISTER.md` file locally in the repository.
     - Surface the risk in the generated dated report output. Automatic issue creation remains out of scope for the current MVP.
4. **Trigger Mechanism**:
   - The report generation is triggered at the end of every Conductor Phase. The AI agent executing the phase will invoke the reporting script as a mandatory step in the Phase Completion Protocol.

## Non-Functional Requirements
- Uses the GitHub API / `gh` CLI for secure operations.
- Must execute deterministically and idempotently.

## Out of Scope
- Code linting (handled by CI/CD separately; this track only *reports* on CI/CD success).
