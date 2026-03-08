---
    key: STORY-BILL-001
    title: Billing tables migration (subscriptions, usage_records)
    type: story
    milestone: M9 Billing + quota
    labels: [phase:8-prod, priority:low, size:S, track:billing, type:story]
    ---

    ## Problem

    Need data model for subscription and usage tracking.

    ## Proposed solution

    Add subscriptions and usage_records tables with tenant linkage.

    ## Dependencies

    - EPIC-BILLING — Billing, subscriptions, usage and quota
- TASK-PLAT-P0-TENANTRUN — P0: Add tenant_id to runs and propagate

    ## Acceptance criteria

    - [ ] Migrations create tables with FKs and indexes
- [ ] ORM models exist
- [ ] Autogenerate import wiring works

    ## Test plan

    - [ ] Integration: migrate up/down

    ## Notes / references

    _None_
