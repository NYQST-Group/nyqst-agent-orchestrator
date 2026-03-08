---
    key: STORY-APPS-004
    title: Triggers v1: schedule + event trigger for apps
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:medium, size:L, track:workflows, type:story]
    ---

    ## Problem

    Repeatability requires scheduling and event triggers.

    ## Proposed solution

    Implement scheduler and event trigger dispatcher that calls app runner with specified inputs/context.

    ## Dependencies

    - STORY-APPS-003 — App runner v1: start run, stream events, persist outputs
- EPIC-WORKFLOWS — Workflow builder + triggers + schedules (n8n-like)

    ## Acceptance criteria

    - [ ] Cron schedule triggers app run
- [ ] Bundle version created triggers app run (configured)
- [ ] Trigger runs are audited with run logs

    ## Test plan

    - [ ] Integration: trigger fires and creates run

    ## Notes / references

    _None_
