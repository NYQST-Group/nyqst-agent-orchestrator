---
    key: STORY-DOCS-001
    title: Backend: bundles + versions data model and migrations
    type: story
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:critical, size:M, track:documents, type:story]
    ---

    ## Problem

    We need canonical document objects with versioning to attach provenance.

    ## Proposed solution

    Add tables for bundles and bundle_versions (and bundle_files if needed), linking to artifacts and runs.

    ## Dependencies

    - EPIC-DOCUMENTS — Document management (bundles, versions, ingest, diff)
- EPIC-PLATFORM — Platform baseline, core primitives, and CI
- TASK-CON-004 — Implement bundle/version + evidence + insight schemas + fixtures

    ## Acceptance criteria

    - [ ] Bundle and BundleVersion tables exist with project/tenant scoping
- [ ] Version increments are enforced per bundle
- [ ] BundleVersion links to ingest run and artifact ids
- [ ] Migrations are reversible where possible

    ## Test plan

    - [ ] Integration: create bundle, add version, query versions

    ## Notes / references

    _None_
