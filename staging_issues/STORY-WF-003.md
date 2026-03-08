---
    key: STORY-WF-003
    title: Scheduler/triggers: schedule + event triggers for workflows
    type: story
    milestone: M8 Workflows + triggers
    labels: [phase:7-workflows, priority:medium, size:L, track:workflows, type:story]
    ---

    ## Problem

    Automation needs triggers; manual-only workflows don't scale.

    ## Proposed solution

    Implement trigger dispatcher for schedules and project events (bundle version created, validation failed).

    ## Dependencies

    - STORY-WF-002 — Workflow runner: node execution + logs + retries
- STORY-APPS-004 — Triggers v1: schedule + event trigger for apps

    ## Acceptance criteria

    - [ ] Schedule triggers fire
- [ ] Event triggers fire
- [ ] Trigger events create audited runs

    ## Test plan

    - [ ] Integration: trigger simulation

    ## Notes / references

    _None_
