# [NX-011] Knowledge base manager v1 (Dify-style): ingestion, chunking policy, reindex, doc status

**Goal**
Provide an operator/user UI for managing “knowledge bases”:
- upload docs into a KB
- set chunking + embedding policy
- show indexing status + errors
- reindex / delete
- evaluate retrieval quality

**Leverage**
- Existing document upload + RAG/OpenSearch services.
- Existing pointers/manifests for storing KB membership manifests.

**Implementation**
Backend:
- KB model (tenant_id, name, description, config JSON)
- membership links (kb_id → pointer_id or document_id)
- indexing job queue + status table

Frontend:
- Knowledge Bases page:
  - list KBs
  - create KB
  - view documents, index status, reindex

**Acceptance criteria**
- A KB can be created and used by an agent as its retrieval scope.
- Index status is visible and actionable.

