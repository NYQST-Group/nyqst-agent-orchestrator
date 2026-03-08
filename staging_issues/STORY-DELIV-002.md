---
    key: STORY-DELIV-002
    title: Co-generation jobs (website + report) with pending entities flag
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:medium, size:L, track:platform, type:story]
    ---

    ## Problem

    Some deliverables require async generation; UI must not show complete prematurely.

    ## Proposed solution

    Implement async entity pipeline; done event includes has_async_entities_pending and UI polls until complete.

    ## Dependencies

    - EPIC-DELIVERABLES — Deliverables pipeline (reports/websites) + co-generation + diff
- TASK-PLAT-P0-ARQ — P0: Fix arq worker registration + Redis always-on
- TASK-CON-002 — Implement run_event schema + fixtures + validators

    ## Acceptance criteria

    - [ ] Co-generation workflow schedules async jobs
- [ ] done event includes pending flag when appropriate
- [ ] Frontend continues polling and updates UI when pending resolves

    ## Test plan

    - [ ] Integration: async job completes and clears pending
- [ ] E2E: pending indicator behavior

    ## Notes / references

    _None_
