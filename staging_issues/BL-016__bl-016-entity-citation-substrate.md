# [BL-016] Entity/Citation Substrate
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:high`, `track:infrastructure`, `size:M`
**Milestone:** M2: Deliverables
**Blocked By:** BL-002, MIG-0005A (entity_type + tags columns)
**Blocks:** BL-011

**Body:**
## Overview
Complete the entity/citation service layer on top of the Artifact model. Migration 0005 (Phase 0) adds entity_type and tags columns to Artifact. This task builds the service that creates entity artifacts from REFERENCES_FOUND events, provides deduplication via URL hashing, and exposes a per-run entities API endpoint. Entity creation runs asynchronously via the existing arq + Redis job queue.

> **Note:** BL-005 is a soft dependency for citation-binding integration testing only.

## Acceptance Criteria
- [ ] `create_entity_artifact(url, title, snippet, entity_type)` helper in ArtifactService
- [ ] Deduplication: entity artifacts keyed by sha256 of canonical URL in `tags["canonical_id"]`
- [ ] Async entity creation: REFERENCES_FOUND event dispatches arq background job
- [ ] `GET /api/v1/runs/{run_id}/entities` returns entities grouped by entity_type
- [ ] Citation IDs in generated reports resolve to entity artifacts
- [ ] Existing artifact operations unaffected

## Technical Notes
- Extends: `src/intelli/services/substrate/artifact_service.py`
- New endpoint in: `src/intelli/api/v1/runs.py`
- Async job in: `src/intelli/core/jobs.py` (arq + Redis already configured)
- ArtifactEntityType enum: WEB_SOURCE, API_DATA, GENERATED_CONTENT, GENERATED_REPORT, GENERATED_WEBSITE, GENERATED_PRESENTATION, GENERATED_DOCUMENT, KNOWLEDGE_BASE, USER_UPLOAD, CITATION_BUNDLE
- Decision: extend Artifact with entity_type field (not new table) -- avoids schema proliferation

## References
- BACKLOG.md: BL-016
- IMPLEMENTATION-PLAN.md: Section 2.2

---

### Wave 2: Depends on BL-001 (orchestrator) and/or BL-004 (markup AST)

---