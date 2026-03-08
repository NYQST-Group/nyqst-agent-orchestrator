---
    key: STORY-WF-004
    title: Frontend: workflow builder UI (node canvas) + run logs
    type: story
    milestone: M8 Workflows + triggers
    labels: [phase:7-workflows, priority:medium, size:XL, track:frontend, type:story]
    ---

    ## Problem

    Users need to build workflows visually (n8n-style) and debug them.

    ## Proposed solution

    Implement workflow builder UI: node palette, edge creation, node config, validation warnings, and run log viewer.

    ## Dependencies

    - STORY-WF-001 — Backend: workflow definitions + versioning + API
- STORY-FE-001 — Implement app shell: routing + left nav + project selector

    ## Acceptance criteria

    - [ ] Create workflow graph via UI
- [ ] Configure node ops (run app, ingest bundle, validate, notify)
- [ ] View run logs per node
- [ ] Publish workflow version

    ## Test plan

    - [ ] Vitest: workflow builder store
- [ ] E2E: create workflow and publish

    ## Notes / references

    _None_
