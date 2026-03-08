---
    key: STORY-DOCS-004
    title: Pipeline: extraction to structured JSON + evidence spans
    type: story
    milestone: M2 Documents (bundles/versions/ingest/diff)
    labels: [phase:2-documents, priority:high, size:L, track:documents, type:story]
    ---

    ## Problem

    To make NotebookLM-style intelligence, we need structured extraction that links to evidence spans.

    ## Proposed solution

    Implement extraction stage producing structured JSON artifact plus evidence objects with spans and confidence.

    ## Dependencies

    - STORY-DOCS-003 — Pipeline: ingest runner (parse/normalize/chunk/index) with run logs
- EPIC-INTEL — Evidence + insights + audit-first provenance

    ## Acceptance criteria

    - [ ] Extraction output stored as artifact linked to bundle_version
- [ ] Evidence records created with source spans and confidence
- [ ] Failures degrade gracefully (partial output + errors surfaced)
- [ ] Extraction is idempotent and re-runnable

    ## Test plan

    - [ ] Integration: extraction fixtures
- [ ] Unit: span mapping logic

    ## Notes / references

    _None_
