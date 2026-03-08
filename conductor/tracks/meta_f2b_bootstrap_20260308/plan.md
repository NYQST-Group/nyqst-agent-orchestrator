# Implementation Plan: Meta-Track - F2B Project Lifecycle & Infrastructure

## Phase 1: V4 Plan Alignment & GitHub Initialization (Week 1) [checkpoint: d584c7c]
- [x] Task: Review and lock V4 Epics against current codebase constraints 149a129
  - [x] Sub-task: Identify any discrepancies between V4 specs and existing repo
  - [x] Sub-task: Finalize Epic priorities for M0 and M0.5
- [x] Task: Initialize Target GitHub Repository 5d9682f
  - [x] Sub-task: Create empty repository on GitHub and configure access
  - [x] Sub-task: Push existing local repository to GitHub `main` branch
  - [x] Sub-task: Commit and push the initial `conductor/` setup
- [x] Task: Issue & Milestone Migration 7829ff2
  - [x] Sub-task: Create GitHub Milestones based on `EPIC_STRUCTURE.md`
  - [x] Sub-task: Run issue import scripts using the master manifest `staging_issues/v4_final_import.json`
  - [x] Sub-task: Import 45 new issues from `V4_NEW_ISSUES.md`
- [x] Task: Conductor - User Manual Verification 'Phase 1: V4 Plan Alignment & GitHub Initialization' (Protocol in workflow.md) d584c7c

## Phase 2: Conductor & GitHub Synchronization (Week 1) [checkpoint: 0916ff1]
- [x] Task: Build Sync Script (`sync-conductor.sh`) ed574f3
  - [x] Sub-task: Write parser for `conductor/tracks/*/plan.md` tasks
  - [x] Sub-task: Implement `gh issue view` calls to check remote state
  - [x] Sub-task: Implement `gh issue close` for locally completed tasks
- [x] Task: Automate Sync Execution 6513e10
  - [x] Sub-task: Hook script into Git `pre-commit` or `post-commit`
  - [x] Sub-task: Ensure the workflow strictly requires issue IDs on tasks
- [x] Task: Conductor - User Manual Verification 'Phase 2: Conductor & GitHub Synchronization' (Protocol in workflow.md) 0916ff1

## Phase 3: F2B Lifecycle & Infrastructure Bootstrap (Week 2) [checkpoint: ecaacd8]
- [x] Task: Establish Environments & Configurations e0f1c38
  - [x] Sub-task: Define `.env` templates for Dev, Staging, and Prod
  - [x] Sub-task: Validate Docker Compose for local PostgreSQL+pgvector and Redis
- [x] Task: CI/CD Pipeline Configuration (V4-INFRA-001) 9b5f152
  - [x] Sub-task: Create GitHub Actions workflow for Python `pytest` and linting
  - [x] Sub-task: Create GitHub Actions workflow for TS `vitest` and type-checking
  - [x] Sub-task: Enforce branch protection rules blocking merges on failing CI
- [x] Task: Conductor - User Manual Verification 'Phase 3: F2B Lifecycle & Infrastructure Bootstrap' (Protocol in workflow.md) ecaacd8

## Phase 4: Core Contracts & Hygiene Alignment (Week 2)
- [ ] Task: Audit existing base contracts against V4 specifications (EPIC-CONTRACTS)
  - [ ] Sub-task: Validate existing `RunEvents` schema
  - [ ] Sub-task: Validate baseline tenant-isolation fields (e.g., `tenant_id`)
  - [ ] Sub-task: Ensure PR templates require Contract review for schema changes
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Core Contracts & Hygiene Alignment' (Protocol in workflow.md)