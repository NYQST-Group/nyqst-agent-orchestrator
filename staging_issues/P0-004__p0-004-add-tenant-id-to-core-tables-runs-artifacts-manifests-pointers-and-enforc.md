# [P0-004] Add tenant_id to core tables (runs, artifacts, manifests, pointers) and enforce isolation

**Why this matters**
Tenant isolation cannot be “added later” if core tables don’t carry tenant identity. It is a design constraint for enterprise controls, quotas, and data access.

**Repo evidence**
- Tenant model exists (e.g., `src/intelli/db/models/tenants.py`), but `Run` and substrate tables do not include `tenant_id`.

**Goal**
- Every core record is tenant-scoped and queries enforce tenant filters.

**Implementation**
1. Create a migration (suggested `0005d_add_tenant_id_to_core_tables.py`):
   - Add `tenant_id` FK columns to `runs`, `artifacts`, `manifests`, `pointers` (and other high-risk tables).
   - Backfill tenant_id via workspace/session where possible; otherwise default to a “system” tenant and document.
2. Update repositories/services to require `tenant_id` context and enforce it in queries.
3. Update API layer to derive tenant_id from auth context (JWT claims / session) and pass through.
4. Add tests: cross-tenant access denied.

**Acceptance criteria**
- It is impossible to query a run/artifact from another tenant through service/repo APIs.
- Migration backfill is safe and idempotent.
