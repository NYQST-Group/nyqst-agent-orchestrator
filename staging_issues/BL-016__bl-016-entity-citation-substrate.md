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
- Async job in: `src/intelli/core/jobs.py` — **arq + Redis wired but worker operational status unverified (Phase 0 checklist item, SC-01/DEC-017). Verify before implementing.**
- ArtifactEntityType enum: WEB_SOURCE, API_DATA, GENERATED_CONTENT, GENERATED_REPORT, GENERATED_WEBSITE, GENERATED_PRESENTATION, GENERATED_DOCUMENT, KNOWLEDGE_BASE, USER_UPLOAD, CITATION_BUNDLE
- Decision: extend Artifact with entity_type field (not new table) -- avoids schema proliferation

## Async Entity Worker Sub-Task (GAP-081)

BL-016 is not complete until the async entity creation worker is operational. This is a required follow-on:

**BL-016-ASYNC: Async Entity Creation Worker**
- Implement arq background job in `src/intelli/core/jobs.py`: `process_entity_creation_job(run_id: str, entity_data: list[dict])`
- Job triggered when `has_async_entities_pending: true` is set in the `done` SSE event
- Job logic: (1) resolve entity deduplication (SHA-256 of canonical URL); (2) write Artifact records with entity_type; (3) emit `references_found` SSE event via PG NOTIFY after completion
- `WorkerSettings` class must declare `functions = [process_entity_creation_job]`
- Size: ~1 SP
- Blocked by: arq worker operational verification (Phase 0 checklist)

## Entity Reference Algorithm (GAP-085)

The following algorithm governs entity deduplication, citation assignment, and cross-type reference resolution:

**1. Primary deduplication key**: SHA-256 of the content (for web pages: SHA-256 of the canonical URL after normalization)

**2. URL normalization for web sources**: before hashing, apply:
- Remove query parameters that are tracking-only (`utm_*`, `fbclid`, `gclid`, etc.)
- Strip trailing slash
- Lowercase the domain
- Resolve HTTP → HTTPS
- Example: `http://Example.com/page/?utm_source=brave` → `https://example.com/page/`

**3. Citation identifier**: UUID assigned at entity creation time, stored in `entity.metadata["citation_identifier"]`. This UUID is used by GML `<gml-inlinecitation identifier="..."/>` tags for citation binding.

**4. GML citation binding**:
```python
def resolve_citation(identifier: str, entity_registry: dict[str, Entity]) -> Entity | None:
    """
    Resolve a GML inline citation identifier to the backing entity.
    identifier: the UUID from <gml-inlinecitation identifier="UUID"/>
    """
    return entity_registry.get(identifier)  # keyed by citation_identifier UUID
```

**5. Cross-type references**: Tool output entities (WEB_SOURCE, API_DATA) and deliverable entities (GENERATED_REPORT, GENERATED_WEBSITE, etc.) share the same `artifacts` table, differentiated by the `entity_type` column (added in Migration 0005a per DEC-055). No separate entity table. Citation IDs work across entity types.

**6. Deduplication check** (in `create_entity_artifact`):
```python
async def create_entity_artifact(db, url: str, title: str, snippet: str, entity_type: str) -> Artifact:
    canonical_url = normalize_url(url)
    content_hash = sha256(canonical_url.encode()).hexdigest()

    # Check for existing entity with same content hash
    existing = await ArtifactRepository.get_by_sha256(db, content_hash)
    if existing:
        return existing  # Deduplicated — same source retrieved twice

    citation_id = str(uuid4())
    artifact = Artifact(
        sha256=content_hash,
        media_type="application/vnd.nyqst.entity+json",
        entity_type=entity_type,
        metadata={"citation_identifier": citation_id, "url": canonical_url, "title": title, "snippet": snippet}
    )
    return await ArtifactRepository.create(db, artifact)
```

## References
- BACKLOG.md: BL-016
- IMPLEMENTATION-PLAN.md: Section 2.2
- GAP-085 (entity reference algorithm)

---

### Wave 2: Depends on BL-001 (orchestrator) and/or BL-004 (markup AST)

---