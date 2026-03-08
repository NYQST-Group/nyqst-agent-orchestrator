---
    key: STORY-BILL-002
    title: Usage recording on run completion
    type: story
    milestone: M9 Billing + quota
    labels: [phase:8-prod, priority:low, size:M, track:billing, type:story]
    ---

    ## Problem

    Quota and billing depend on accurate usage records per run.

    ## Proposed solution

    Create usage service to record cost/tokens per run, linked to tenant.

    ## Dependencies

    - STORY-BILL-001 — Billing tables migration (subscriptions, usage_records)
- TASK-CON-002 — Implement run_event schema + fixtures + validators

    ## Acceptance criteria

    - [ ] Usage record created when run completes
- [ ] Usage aggregates per month
- [ ] No duplication on retries

    ## Test plan

    - [ ] Integration: run completion creates one usage record

    ## Notes / references

    _None_
