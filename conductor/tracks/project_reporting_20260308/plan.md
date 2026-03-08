# Implementation Plan: Project Meta-Reporting & Health Tracking

## Phase 1: GitHub Project View Design & Provisioning (Week 1)
- [ ] Task: Design the Meta-Reporting Dashboard schema
  - [ ] Sub-task: Define custom fields required for the GitHub Project (e.g., Phase Status, Coverage, Blocked Boolean, Process Health)
  - [ ] Sub-task: Document the configuration for the GitHub Project views (Kanban, Table, and Health Dashboard)
- [ ] Task: Provision GitHub Project Board
  - [ ] Sub-task: Script the creation of the Project V2 using `gh project create` (or instruct user to manually configure the designed schema)
  - [ ] Sub-task: Ensure the repository is linked to the new Project View
- [ ] Task: Conductor - User Manual Verification 'Phase 1: GitHub Project View Design & Provisioning' (Protocol in workflow.md)

## Phase 2: Data Aggregation Engine (Week 1)
- [ ] Task: Build Conductor progress parser
  - [ ] Sub-task: Write Tests for markdown regex parsing of `[x]` vs `[ ]`
  - [ ] Sub-task: Implement script to output Phase completion percentages
- [ ] Task: Build CI/CD & Issue state extractors
  - [ ] Sub-task: Write script to fetch latest Pytest/Vitest coverage numbers from artifacts
  - [ ] Sub-task: Write script to query `gh issue list` and calculate burn-down metrics
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Data Aggregation Engine' (Protocol in workflow.md)

## Phase 3: Meta-Issue Rules Engine & Risk Register (Week 2)
- [ ] Task: Implement Risk Evaluation Logic
  - [ ] Sub-task: Write Tests for evaluation rules (e.g., Coverage < 80% returns RISK)
  - [ ] Sub-task: Implement `evaluate_hygiene()` function combining the three data sources
- [ ] Task: Automate Actionable Outputs
  - [ ] Sub-task: Implement `gh issue create` wrapper to dynamically raise `meta-risk` issues if rules fail
  - [ ] Sub-task: Implement local `RISK_REGISTER.md` update logic (append warnings with timestamps)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Meta-Issue Rules Engine & Risk Register' (Protocol in workflow.md)

## Phase 4: Workflow Integration (Week 2)
- [ ] Task: Build the master `generate_report.sh` orchestrator
  - [ ] Sub-task: Combine data aggregation, evaluation, and GitHub Project mutation into a single script
- [ ] Task: Update Conductor Protocol
  - [ ] Sub-task: Modify `conductor/workflow.md` to formally require the execution of `generate_report.sh` at the end of the "Phase Completion Verification" protocol.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Workflow Integration' (Protocol in workflow.md)