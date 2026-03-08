# Specification: Meta-Track: F2B Project Lifecycle, Alignment & Infrastructure

## Objective
Before diving into product features, we must establish a comprehensive Meta-Track that ensures alignment across all disciplines. This track governs the Front-to-Back (F2B) project lifecycle, aligns the V4 delivery plan with reality, bootstraps local and CI/CD infrastructure, and ensures tight coupling between GitHub Issues and Conductor plans.

## Key Deliverables
1. **Plan Alignment & GitHub Initialization**: Verify V4 Build Pack epics, initialize the remote repository, and migrate all issues/milestones so GitHub acts as the remote source of truth.
2. **Conductor-GitHub Sync Mechanism**: Implement automated syncing (`sync-conductor.sh`) so local `[x]` checkmarks resolve remote GitHub issues.
3. **F2B Lifecycle Definition**: Document and enforce branching strategies, environment progression (Dev, Staging, Prod), and the Definition of Done (DoD).
4. **Infrastructure & CI/CD Bootstrap**: Establish Docker environments, databases (PostgreSQL/Redis), and GitHub Actions pipelines to block bad merges.
5. **Contract Baseline Alignment**: Review and lock the initial API/Event contracts (Schemas, Pydantic, TS) to unblock parallel track development.

## Rationale
Proceeding without this meta-track risks parallel streams colliding due to misaligned contracts, broken build pipelines, or diverging issue trackers. This track guarantees that the "machinery" of delivery is fully operational.