---
    key: STORY-CRM-001
    title: Backend: CRM entities + relationships tables and API
    type: story
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:medium, size:M, track:intelligence, type:story]
    ---

    ## Problem

    CRM entities anchor intelligence in real-world objects.

    ## Proposed solution

    Implement entity CRUD with relationship edges and tenant/project scoping.

    ## Dependencies

    - EPIC-CRM — CRM entities, relationships, and timelines
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Entity CRUD endpoints exist
- [ ] Relationship edges stored and queryable
- [ ] Tenant/project scoping enforced

    ## Test plan

    - [ ] Integration: create entity + relationship

    ## Notes / references

    _None_
