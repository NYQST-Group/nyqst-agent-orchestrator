# Specification: Meta-Track: F2B Project Lifecycle, Alignment & Infrastructure

## Rectification Note
This specification is preserved as historical intent. As of March 11, 2026, the validated outcome is partial: the repository/bootstrap and CI guardrails landed, but the Conductor/GitHub sync mechanism is now explicitly read-only and tenant-isolation contract alignment remains incomplete until `tenant_id` is present on the core run/substrate tables and the related GitHub work is closed.

## Objective
Before diving into product features, we must establish a comprehensive Meta-Track that ensures alignment across all disciplines. This track governs the Front-to-Back (F2B) project lifecycle, aligns the V4 delivery plan with reality, bootstraps local and CI/CD infrastructure, and ensures tight coupling between GitHub Issues and Conductor plans.

## Key Deliverables
1. **Plan Alignment & GitHub Initialization**: Verify V4 Build Pack epics, initialize the remote repository, and migrate all issues/milestones so GitHub acts as the remote source of truth.
2. **Conductor-GitHub Sync Mechanism**: Implement automated validation (`sync-conductor.sh`) so local plan state can be compared against remote GitHub issues without mutating issue state.
3. **F2B Lifecycle Definition**: Document and enforce branching strategies, environment progression (Dev, Staging, Prod), and the Definition of Done (DoD).
4. **Infrastructure & CI/CD Bootstrap**: Establish Docker environments, databases (PostgreSQL/Redis), and GitHub Actions pipelines to block bad merges.
5. **Contract Baseline Alignment**: Review and lock the initial API/Event contracts (Schemas, Pydantic, TS) to unblock parallel track development, while explicitly tracking any remaining tenant-isolation gaps as incomplete.

## Rationale
Proceeding without this meta-track risks parallel streams colliding due to misaligned contracts, broken build pipelines, or diverging issue trackers. This track guarantees that the "machinery" of delivery is fully operational.
