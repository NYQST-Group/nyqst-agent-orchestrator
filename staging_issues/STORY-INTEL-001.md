---
    key: STORY-INTEL-001
    title: Backend: evidence model + API + provenance enforcement
    type: story
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:critical, size:M, track:intelligence, type:story]
    ---

    ## Problem

    Evidence must be first-class and must always have provenance.

    ## Proposed solution

    Create evidence tables/API; enforce source references (bundle version or web snapshot) and run linkage when applicable.

    ## Dependencies

    - EPIC-INTEL — Evidence + insights + audit-first provenance
- TASK-CON-004 — Implement bundle/version + evidence + insight schemas + fixtures
- STORY-DOCS-004 — Pipeline: extraction to structured JSON + evidence spans

    ## Acceptance criteria

    - [ ] Evidence CRUD endpoints exist
- [ ] Evidence requires a source reference
- [ ] Evidence can link to run_id and bundle_version_id
- [ ] Evidence can be attached to insights and model fields

    ## Test plan

    - [ ] Integration: create evidence with source span
- [ ] Authz tests: tenant isolation

    ## Notes / references

    _None_
