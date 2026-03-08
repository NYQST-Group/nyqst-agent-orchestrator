---
    key: STORY-DOCS-005
    title: Diff engine: document diff + extraction diff + impact diff outputs
    type: story
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:high, size:L, track:documents, type:story]
    ---

    ## Problem

    Users must see what changed between versions and why it matters.

    ## Proposed solution

    Compute diffs across text, structured extraction, and downstream impacted model fields/insights.

    ## Dependencies

    - STORY-DOCS-004 — Pipeline: extraction to structured JSON + evidence spans
- EPIC-MODELS — Models + validation + impact diffs

    ## Acceptance criteria

    - [ ] Document diff highlights changed passages
- [ ] Extraction diff shows field-level deltas and confidence changes
- [ ] Impact diff lists stale insights and changed model fields
- [ ] Diff outputs can be represented as artifacts and pinned to canvas

    ## Test plan

    - [ ] Unit: diff algorithms
- [ ] Integration: v1/v2 fixture yields deterministic diffs

    ## Notes / references

    _None_
