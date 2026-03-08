---
    key: STORY-FE-003
    title: Runs screens v1 (list + run detail timeline) fixture-driven
    type: story
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:medium, size:M, track:frontend, type:story]
    ---

    ## Problem

    Audit is non-negotiable; run timeline UI must exist early.

    ## Proposed solution

    Implement Runs list and Run detail timeline renderer driven by run_event fixtures.

    ## Dependencies

    - STORY-FE-001 — Implement app shell: routing + left nav + project selector
- TASK-CON-002 — Implement run_event schema + fixtures + validators

    ## Acceptance criteria

    - [ ] Runs list shows kind/status/duration/cost
- [ ] Run detail renders ordered events and handles unknown event types gracefully
- [ ] Artifacts produced are shown in sidebar
- [ ] Error and warning events are visible

    ## Test plan

    - [ ] Vitest: timeline renderer
- [ ] Playwright smoke open run detail

    ## Notes / references

    _None_
