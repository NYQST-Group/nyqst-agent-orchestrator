# Implementation Plan: Tracks 1-4 Rectification & Repo-First Reporting

## Phase 1: Historical Validation & Status Correction (Week 1)
- [x] Task: Validate the current state of Tracks 1-4 against the repository and GitHub
  - [x] Sub-task: Confirm repo bootstrap, issue import, milestones, and branch protection status
  - [x] Sub-task: Identify inaccurate completion claims and remaining gaps
- [x] Task: Annotate historical track documents and metadata
  - [x] Sub-task: Add rectification notes to the first four tracks
  - [x] Sub-task: Update statuses from generic `new` values to accurate corrected states

## Phase 2: Sync and Reporting Rectification (Week 1)
- [x] Task: Replace Conductor issue mutation with read-only validation
  - [x] Sub-task: Update `sync-conductor.sh` to fail on drift, missing mappings, or command failures
  - [x] Sub-task: Establish `conductor/task_issue_map.json` as the sidecar mapping surface for future work
- [x] Task: Implement repo-first reporting outputs
  - [x] Sub-task: Generate dated Markdown and JSON health reports under `reports/project_health/`
  - [x] Sub-task: Update `RISK_REGISTER.md` from deterministic rules

## Phase 3: Provenance and Incident Preservation (Week 1)
- [x] Task: Add sanitization provenance manifests
  - [x] Sub-task: Write `staging_issues/SANITIZATION_MANIFEST.md`
  - [x] Sub-task: Write `staging_issues/SANITIZATION_MANIFEST.json`
- [x] Task: Preserve the branch-protection incident and recovery path
  - [x] Sub-task: Add a repo-local incident note for the March 8, 2026 branch-protection failure mode
  - [x] Sub-task: Mark the mocked contract publisher claim as partial until implemented or removed
