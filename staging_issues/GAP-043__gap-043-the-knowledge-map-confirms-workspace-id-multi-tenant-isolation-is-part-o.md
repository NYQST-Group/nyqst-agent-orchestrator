# [GAP-043] The KNOWLEDGE-MAP confirms `workspace_id` (multi-tenant isolation) is part of all streaming events. The platform has `tenant_id` in the auth system. However, there is no document specifying the row-level security (RLS) strategy for the database, the tenant isolation guarantee for SSE streams (ensuring tenant A cannot receive tenant B's events), or the isolation of LangGraph checkpoints by tenant. For an enterprise product, this is a compliance requirement, not a nice-to-have.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-043
- **Severity**: MEDIUM
- **Description**: The KNOWLEDGE-MAP confirms `workspace_id` (multi-tenant isolation) is part of all streaming events. The platform has `tenant_id` in the auth system. However, there is no document specifying the row-level security (RLS) strategy for the database, the tenant isolation guarantee for SSE streams (ensuring tenant A cannot receive tenant B's events), or the isolation of LangGraph checkpoints by tenant. For an enterprise product, this is a compliance requirement, not a nice-to-have.
- **Affected BL Items**: BL-001 (orchestrator must be tenant-scoped), all data models
- **Source Evidence**: KNOWLEDGE-MAP (workspace_id in all events); streaming-events-extract.md (X-Gradient-Workspace-Id header); PLATFORM-FRAMING.md Layer 3 (multi-tenant isolation listed as Layer 3 concern)
- **Resolution**: Define v1 tenant isolation: (1) All DB queries include `WHERE tenant_id = $current_tenant` (application-level isolation); (2) LangGraph `thread_id` includes `{tenant_id}:{run_id}` to prevent checkpoint namespace collisions; (3) SSE channels namespaced as `run_stream_{tenant_id}_{run_id}` in NOTIFY; (4) Document that PostgreSQL RLS is a Layer 3 enhancement (stronger isolation with row-level policies). Add to BL-001 technical notes.
- **Owner Recommendation**: Architecture lead
- **Wave**: W0 — must be specified before BL-001 implementation

---

### GAP-044 — No Data Retention or Backup Policy