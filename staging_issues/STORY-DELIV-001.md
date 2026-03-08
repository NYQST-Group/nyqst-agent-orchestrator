---
    key: STORY-DELIV-001
    title: Deliverable selection UI + artifact persistence
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:M, track:frontend, type:story]
    ---

    ## Problem

    Users need to choose deliverables and see generation status and outputs.

    ## Proposed solution

    Implement deliverable selector UI (report/website/etc), persist deliverable artifacts, and show previews.

    ## Dependencies

    - EPIC-DELIVERABLES — Deliverables pipeline (reports/websites) + co-generation + diff
- EPIC-GENUI — GenUI renderer (component registry, GML, charts) for dynamic outputs
- STORY-APPS-003 — App runner v1: start run, stream events, persist outputs

    ## Acceptance criteria

    - [ ] User can select a deliverable type and start generation
- [ ] Generation emits events visible in UI
- [ ] Final deliverable artifact viewable and downloadable

    ## Test plan

    - [ ] E2E: generate report deliverable from fixture

    ## Notes / references

    _None_
