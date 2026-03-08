---
    key: STORY-STUDIO-004
    title: Pinning: pin app outputs and diffs into canvas + notebook
    type: story
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:high, size:M, track:studio, type:story]
    ---

    ## Problem

    Pinning is how work becomes reusable and shareable.

    ## Proposed solution

    Implement pin actions from Apps and Documents into Studio surfaces with provenance.

    ## Dependencies

    - EPIC-APPS — Apps system (Dify-style) + context packs + runs
- STORY-DOCS-005 — Diff engine: document diff + extraction diff + impact diff outputs
- STORY-STUDIO-002 — Canvas v1: pan/zoom, blocks, edges, inspector

    ## Acceptance criteria

    - [ ] Pin app output creates canvas block linked to run
- [ ] Pin diff creates diff block linked to bundle versions
- [ ] Pinning can also create a notebook page/section

    ## Test plan

    - [ ] E2E: run app (fixture) then pin to canvas

    ## Notes / references

    _None_
