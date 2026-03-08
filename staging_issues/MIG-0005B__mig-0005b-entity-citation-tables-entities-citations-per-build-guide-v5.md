# [MIG-0005B] Entity + Citation tables (entities, citations) per Build Guide v5

**Purpose**
Persist entities/claims/citations so sources are not ephemeral chat output.

**Target schema (suggested)**
- `entities`:
  - `id` UUID PK
  - `run_id` UUID FK (nullable, for run-scoped entities)
  - `artifact_id` UUID FK (nullable, for artifact-scoped entities)
  - `type` TEXT (Claim, Source, Chunk, Finding, Person, Company, etc.)
  - `label` TEXT
  - `data` JSONB (arbitrary attributes; include provenance fields)
  - timestamps
- `citations`:
  - `id` UUID PK
  - `entity_id` FK
  - `artifact_id` FK (what is being cited)
  - `locator` JSONB (page, offsets, chunk_id, quote hash)
  - `confidence` FLOAT
  - timestamps

**Acceptance criteria**
- Migration applies cleanly.
- Minimal CRUD service exists (even if API comes later) to write/read entities.
- One integration test: create run → emit entity + citation → read back.

