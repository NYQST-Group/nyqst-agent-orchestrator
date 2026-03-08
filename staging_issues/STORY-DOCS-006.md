---
    key: STORY-DOCS-006
    title: Frontend: Documents screens (bundles list, detail, version compare)
    type: story
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:high, size:L, track:frontend, type:story]
    ---

    ## Problem

    Documents UI must support upload, status, versions, and compare.

    ## Proposed solution

    Implement Documents screens aligned to contract fixtures then wire to API.

    ## Dependencies

    - STORY-FE-001 — Implement app shell: routing + left nav + project selector
- TASK-CON-004 — Implement bundle/version + evidence + insight schemas + fixtures
- STORY-DOCS-001 — Backend: bundles + versions data model and migrations

    ## Acceptance criteria

    - [ ] Bundles list renders and supports basic search/filter
- [ ] Bundle detail shows version list and processing status
- [ ] Compare view shows diff tabs (doc/extraction/impact)
- [ ] Users can pin diffs to Studio (calls stub handler)

    ## Test plan

    - [ ] Vitest: documents screens
- [ ] E2E: upload + open compare (later when API wired)

    ## Notes / references

    _None_
