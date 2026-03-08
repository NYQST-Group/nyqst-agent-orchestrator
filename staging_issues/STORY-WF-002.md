---
    key: STORY-WF-002
    title: Workflow runner: node execution + logs + retries
    type: story
    milestone: M8 Workflows + triggers
    labels: [phase:7-workflows, priority:high, size:XL, track:workflows, type:story]
    ---

    ## Problem

    Workflow value comes from reliable execution with node-level visibility and retries.

    ## Proposed solution

    Implement workflow runner using worker/jobs; each node emits events and stores node-run records.

    ## Dependencies

    - STORY-WF-001 — Backend: workflow definitions + versioning + API
- TASK-PLAT-P0-ARQ — P0: Fix arq worker registration + Redis always-on
- TASK-CON-002 — Implement run_event schema + fixtures + validators

    ## Acceptance criteria

    - [ ] Runner executes a workflow graph deterministically
- [ ] Node logs visible and linked to overall run
- [ ] Retries supported per-node with backoff
- [ ] Partial success recorded

    ## Test plan

    - [ ] Integration: execute workflow template on fixtures

    ## Notes / references

    _None_
