---
    key: EPIC-DOCUMENTS
    title: Document management (bundles, versions, ingest, diff)
    type: epic
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:critical, size:XL, track:documents, type:epic]
    ---

    ## Problem

    Documents are the foundation. Everything must attach to bundle versions and be diffable.

    ## Proposed solution

    Implement bundle/version data model, ingest pipeline, extraction outputs, and diff surfaces; wire into UI.

    ## Dependencies

    - EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] Bundles and versions are stored and retrievable
- [ ] Ingest pipeline produces normalized text + extraction outputs
- [ ] Diff view shows document diff + extraction diff + impact diff
- [ ] Every extraction output links to source spans and run id

    ## Test plan

    - [ ] Integration tests: upload bundle, ingest pipeline completes on fixtures
- [ ] Unit tests: diff algorithms
- [ ] E2E: upload v1 then v2 then open diff view

    ## Notes / references

    - See docs/02_USER_FLOWS_MASTER.md Flow 1
