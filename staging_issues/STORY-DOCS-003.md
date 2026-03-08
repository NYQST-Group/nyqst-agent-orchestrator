---
    key: STORY-DOCS-003
    title: Pipeline: ingest runner (parse/normalize/chunk/index) with run logs
    type: story
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:critical, size:L, track:documents, type:story]
    ---

    ## Problem

    Ingest must be reliable, resumable, and observable.

    ## Proposed solution

    Implement ingest pipeline as jobs (worker) emitting RunEvents for progress and producing normalized artifacts and index entries.

    ## Dependencies

    - TASK-PLAT-P0-ARQ — P0: Fix arq worker registration + Redis always-on
- STORY-DOCS-002 — Backend: bundle upload API and artifact storage integration

    ## Acceptance criteria

    - [ ] Ingest pipeline runs async via worker
- [ ] Pipeline emits structured RunEvents (start/step/progress/complete)
- [ ] Normalized text artifacts created and linked to bundle_version
- [ ] Index backend is updated (OpenSearch or pgvector)

    ## Test plan

    - [ ] Integration: ingest pipeline on fixtures
- [ ] Contract: ingest event stream fixture

    ## Notes / references

    _None_
