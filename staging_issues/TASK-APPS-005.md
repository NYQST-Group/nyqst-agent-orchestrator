---
    key: TASK-APPS-005
    title: App diff UI: compare v1 vs v2 config
    type: task
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:medium, size:M, track:frontend, type:task]
    ---

    ## Problem

    Users need to understand what changed between app versions.

    ## Proposed solution

    Implement diff view for app config: inputs/context/engine/outputs/triggers.

    ## Dependencies

    - STORY-APPS-001 — Backend: apps + app_versions + app_runs data model and API
- STORY-APPS-002 — Frontend: App builder wizard (template → publish)

    ## Acceptance criteria

    - [ ] Diff view shows changed fields clearly
- [ ] Runs link back to the exact app version
- [ ] User can open previous version read-only

    ## Test plan

    - [ ] Vitest: diff renderer

    ## Notes / references

    _None_
