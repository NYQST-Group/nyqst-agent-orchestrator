---
    key: STORY-DOCS-002
    title: Backend: bundle upload API and artifact storage integration
    type: story
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:critical, size:L, track:documents, type:story]
    ---

    ## Problem

    Upload must create bundle versions and store raw docs reliably.

    ## Proposed solution

    Implement upload endpoints that store files as artifacts (S3/MinIO) and create bundle_version records.

    ## Dependencies

    - STORY-DOCS-001 — Backend: bundles + versions data model and migrations

    ## Acceptance criteria

    - [ ] Upload creates bundle_version and artifact entries
- [ ] Deduping by hash prevents duplicates (or surfaces them)
- [ ] Large uploads supported with clear limits and errors
- [ ] All writes are tenant/project scoped

    ## Test plan

    - [ ] Integration: upload fixture files; assert artifacts exist in storage

    ## Notes / references

    _None_
