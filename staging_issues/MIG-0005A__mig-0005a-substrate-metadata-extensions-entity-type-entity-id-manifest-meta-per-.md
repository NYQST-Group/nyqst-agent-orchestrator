# [MIG-0005A] Substrate metadata extensions (entity_type/entity_id, manifest meta) per Build Guide v5

**Purpose**
Enable first-class linkage between artifacts/manifests and domain entities (runs, documents, bundles, etc.), and carry richer metadata for provenance.

**Repo starting point**
- `src/intelli/db/models/substrate.py`:
  - `Artifact` has `mime_type` + `metadata` but no explicit `entity_type/entity_id`.
  - `Manifest` has `tree` + `message` but no `meta` JSONB field.

**Target changes**
1. Add to `artifacts`:
   - `entity_type` (TEXT, nullable initially)
   - `entity_id` (UUID, nullable initially)
   - optional: `content_type` if you want semantic classification separate from MIME
2. Add to `manifests`:
   - `meta` JSONB (nullable)
3. Consider adding indexes:
   - `(entity_type, entity_id)` on artifacts
4. Update services to accept / populate these fields when creating artifacts/manifests.

**Acceptance criteria**
- Migration applies cleanly on an existing DB.
- Services can create artifacts with `(entity_type, entity_id)` populated.
- No regressions in document upload / ingestion.

**Notes**
This migration is referenced by multiple BL items (planner, entities, deliverables). Treat it as a dependency unlocker.
