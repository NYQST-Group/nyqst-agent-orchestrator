---
    key: STORY-APPS-003
    title: App runner v1: start run, stream events, persist outputs
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:critical, size:XL, track:platform, type:story]
    ---

    ## Problem

    Apps must run and produce artifacts, not just exist as configs.

    ## Proposed solution

    Implement app runner that creates a Run, executes engine (agent/workflow/query/pipeline), streams events, and writes outputs mapping.

    ## Dependencies

    - STORY-APPS-001 — Backend: apps + app_versions + app_runs data model and API
- TASK-CON-002 — Implement run_event schema + fixtures + validators
- EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] Run created with app_version and inputs stored
- [ ] Streaming events emitted and consumable by UI
- [ ] Outputs are written and linked to run (notebook/canvas/evidence/insights)
- [ ] Failures produce run status FAILED and error events

    ## Test plan

    - [ ] Integration: run app with mocked engine produces artifacts
- [ ] Contract: event stream matches fixtures

    ## Notes / references

    _None_
