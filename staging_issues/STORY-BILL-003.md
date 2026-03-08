---
    key: STORY-BILL-003
    title: Quota middleware blocks over-limit runs
    type: story
    milestone: M9 Billing + quota
    labels: [phase:8-prod, priority:low, size:S, track:billing, type:story]
    ---

    ## Problem

    Prevent abuse and enforce plan limits.

    ## Proposed solution

    Middleware checks quota before run creation and returns 429 when exceeded.

    ## Dependencies

    - STORY-BILL-002 — Usage recording on run completion

    ## Acceptance criteria

    - [ ] Over-quota tenant gets 429 on run start
- [ ] Under-quota passes
- [ ] Errors are clear to UI

    ## Test plan

    - [ ] Integration: quota enforcement

    ## Notes / references

    _None_
