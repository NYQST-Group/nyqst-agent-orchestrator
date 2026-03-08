# EPIC-W2 — Wave 2 — Deliverables pipelines (report, website, slides, document) + context

- Type: **epic**
- Milestone: `M3-W2`
- Repo alignment: **missing**
- Labels: `milestone:M3`, `wave:2`

## Problem

Beyond in-app report preview, NYQST needs robust deliverable generation pipelines and a context system that can scale from task → workspace with inheritance and background indexing.

## Proposed solution

Add deliverable selection (per user message), implement the deliverable store, then add pipelines for website/slides/document exports. Extend context ingestion + retrieval with inheritance and 'Cursor-like' background indexing.

## Acceptance criteria

- User can select deliverable type per prompt; system stores and serves deliverable artifacts by identifier.
- At least one full end-to-end run can output: in-app report + a slide deck + a downloadable document, with citations.
- Context packs can be created at project/workspace scope and inherited into tasks.

## Test plan

- Integration: deliverable store persists identifiers; arq jobs generate expected artifacts.
- E2E: generate slides + document from the UI; artifacts are downloadable and linked to the run.
