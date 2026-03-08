# [NX-004] NotebookLM-style “Research Notebook” (SurfSense-inspired) using existing substrate primitives

**Goal**
Deliver an opinionated “notebook” workflow:
- upload/attach multiple documents
- auto-summarize and extract entities/claims
- chat with citations grounded in the attached corpus
- keep generated notes as versioned artifacts

**Leverage existing repo**
- Notebooks + pointers exist in UI.
- Artifact/Manifest/Pointer primitives exist in backend.
- RAG/OpenSearch exists.

**Missing**
- Notebook-specific indexing strategy (per-notebook corpus)
- Entity/citation persistence
- UX patterns: “sources on the right”, “notes panel”, “evidence map”

**Implementation**
Backend:
- Add notebook corpus index keying (workspace_id + notebook_id).
- Add endpoints:
  - attach/detach docs to notebook
  - generate notebook summary artifact
  - list extracted entities/claims for notebook
Frontend:
- Notebook workspace view:
  - doc list, notes list, chat pane
  - citations jump-to-source

**Acceptance criteria**
- A notebook can be created, populated with docs, and queried with grounded answers.
- Every answer includes citations that resolve to stored source artifacts.

