---
    key: EPIC-WORKFLOWS
    title: Workflow builder + triggers + schedules (n8n-like)
    type: epic
    milestone: M8 Workflows + triggers
    labels: [phase:7-workflows, priority:medium, size:XL, track:workflows, type:epic]
    ---

    ## Problem

    Automation is needed for scale: ingest, extract, validate, refresh, notify.

    ## Proposed solution

    Implement workflow definitions, runner, builder UI, triggers and schedules, and node-level logs.

    ## Dependencies

    - EPIC-APPS — Apps system (Dify-style) + context packs + runs
- EPIC-DOCUMENTS — Document management (bundles, versions, ingest, diff)
- EPIC-MODELS — Models + validation + impact diffs

    ## Acceptance criteria

    - [ ] Workflows can be created from templates
- [ ] Triggers fire reliably (schedule, event)
- [ ] Node logs visible and linked to runs
- [ ] Retries and partial success supported

    ## Test plan

    - [ ] Integration: workflow runner executes a template with mocks
- [ ] E2E: new bundle version triggers workflow

    ## Notes / references

    _None_
