---
    key: STORY-WF-001
    title: Backend: workflow definitions + versioning + API
    type: story
    milestone: M8 Workflows + triggers
    labels: [phase:7-workflows, priority:medium, size:M, track:workflows, type:story]
    ---

    ## Problem

    Workflows require a stored graph and versioned definitions.

    ## Proposed solution

    Create workflow and workflow_version tables; CRUD API; validation of node graph.

    ## Dependencies

    - EPIC-WORKFLOWS — Workflow builder + triggers + schedules (n8n-like)
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Workflow definitions stored with versioning
- [ ] Graph validation prevents cycles unless allowed
- [ ] Version immutability after publish

    ## Test plan

    - [ ] Integration: create workflow, publish, validate graph

    ## Notes / references

    _None_
