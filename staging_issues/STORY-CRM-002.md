---
    key: STORY-CRM-002
    title: Frontend: CRM list + entity detail + timeline + linked items
    type: story
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:medium, size:L, track:frontend, type:story]
    ---

    ## Problem

    Users need to see evidence/insights per entity and navigate relationships.

    ## Proposed solution

    Implement CRM list and entity detail screens with relationship panel and linked evidence/insights/bundles.

    ## Dependencies

    - STORY-CRM-001 — Backend: CRM entities + relationships tables and API
- STORY-FE-001 — Implement app shell: routing + left nav + project selector

    ## Acceptance criteria

    - [ ] Entity list supports filters
- [ ] Entity detail shows linked bundles, evidence, insights
- [ ] Relationship panel shows connected entities

    ## Test plan

    - [ ] Vitest: CRM screens

    ## Notes / references

    _None_
