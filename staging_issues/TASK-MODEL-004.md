---
    key: TASK-MODEL-004
    title: Impact diff: explain model field changes from doc version diffs
    type: task
    milestone: M6 Models + validation
    labels: [phase:5-models, priority:high, size:L, track:intelligence, type:task]
    ---

    ## Problem

    Users need explainability: what changed in the model and why.

    ## Proposed solution

    Compute model field deltas and link them to evidence deltas and document diffs.

    ## Dependencies

    - STORY-DOCS-005 — Diff engine: document diff + extraction diff + impact diff outputs
- STORY-MODEL-003 — Validation engine v1: rule evaluation + run logs
- TASK-INTEL-004 — Stale propagation engine (doc change → evidence/insight/model stale)

    ## Acceptance criteria

    - [ ] Model field delta list produced for v1→v2
- [ ] Each delta links to evidence/diff blocks
- [ ] Dashboards can consume delta feed (later)

    ## Test plan

    - [ ] Integration: fixture v1/v2 produces deterministic impact diff

    ## Notes / references

    _None_
