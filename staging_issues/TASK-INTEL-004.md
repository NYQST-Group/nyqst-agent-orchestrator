---
    key: TASK-INTEL-004
    title: Stale propagation engine (doc change → evidence/insight/model stale)
    type: task
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:high, size:L, track:intelligence, type:task]
    ---

    ## Problem

    When documents change, downstream intelligence must be flagged and explainable.

    ## Proposed solution

    Build a dependency graph from bundle_version to evidence to insight to model fields, and mark stale when upstream changes.

    ## Dependencies

    - STORY-DOCS-005 — Diff engine: document diff + extraction diff + impact diff outputs
- STORY-INTEL-002 — Backend: insights lifecycle + linkage to evidence/CRM/models

    ## Acceptance criteria

    - [ ] Uploading bundle v2 marks dependent insights stale
- [ ] UI shows stale badges with explanation of upstream delta
- [ ] Stale computation is deterministic and testable

    ## Test plan

    - [ ] Unit: stale propagation logic
- [ ] Integration: stale marks after v2 upload

    ## Notes / references

    _None_
