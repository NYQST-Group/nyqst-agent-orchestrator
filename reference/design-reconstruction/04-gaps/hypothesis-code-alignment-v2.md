# Hypothesis Code Alignment — v2
## Re-Validation Against Actual Source Code Scans

**Re-Validation Date:** 2026-02-20
**Original Hypotheses:** `04-gaps/hypothesis-code-alignment.md` (H5–H8)
**Evidence Sources:**
- `07-source-code/BACKEND-SOURCE-SCAN.md` — 103-file Python backend inventory
- `07-source-code/FRONTEND-SOURCE-SCAN.md` — React/TypeScript frontend inventory
- `01-extracts/orchestration-extract.md` (lines 1-100) — PlanSet/Plan/PlanTask schemas
- `01-extracts/streaming-events-extract.md` (lines 1-100) — 22 Superagent events + 4 proposed

---

## H5: Ground Truth Accuracy

### Original Claims
The PLATFORM-GROUND-TRUTH.md document accurately describes:
1. RunEventType enum (28 members including APPROVAL_* events)
2. LangGraph structure (3-node graph: agent → tools → capture_sources)
3. Artifact model schema (no entity_type, no metadata JSONB)
4. 11 API routers
5. 16 database tables

### Source Code Evidence

#### H5.1: RunEventType Enum
**Source:** `BACKEND-SOURCE-SCAN.md` → `db/models/runs.py`

The backend scan (section 1.3) confirms `RunEventType` is defined in `db/models/runs.py` with `RunStatus` and `RunEventType` enums. The original H5 document at lines 22-55 cited the actual source code showing 28 members including `APPROVAL_REQUESTED`, `APPROVAL_GRANTED`, `APPROVAL_DENIED`.

The backend scan at section 9 (Code Metrics) lists `db.models.runs` as "2 models + 2 enums", consistent with `Run`, `RunEvent`, `RunStatus`, `RunEventType`.

**Verdict for H5.1:** CONFIRMED (28 members, APPROVAL_* present)

#### H5.2: LangGraph 3-Node Structure
**Source:** `BACKEND-SOURCE-SCAN.md` section 5 (Agent/Graph Architecture, lines 448-469) and `BACKEND-SOURCE-SCAN.md` section 1.8

Backend scan section 1.8 (`agents/`):
> `graphs/research_assistant.py` — `ResearchState` (dataclass), `ResearchAssistantGraph` (3-node StateGraph)

Backend scan section 5 graph description:
```
Graph Structure (3 nodes):
1. Agent Node — ChatOpenAI with tools bound; invoke_model + tools_condition
2. ToolNode — Tool execution (search_documents, list_notebooks, get_document_info, compare_manifests)
3. END — Conversation termination
```

CAUTION: The backend scan summary at section 5 lists "END" as node 3, but END is a terminal state, not a real node. The original H5.2 code citation (research_assistant.py lines 159-183) shows three actual nodes: `agent`, `tools`, `capture_sources`. The backend scan section 1.8 header also says "3-node StateGraph", confirming the original H5 count. The section 5 summary is imprecise in listing END instead of `capture_sources`.

**Verdict for H5.2:** CONFIRMED (3 nodes: agent, tools, capture_sources — not agent, tools, END as section 5 loosely states)
**Action:** Note that BACKEND-SOURCE-SCAN.md section 5 incorrectly summarizes the graph nodes. The section 1.8 description is accurate.

#### H5.3: Artifact Model Schema
**Source:** `BACKEND-SOURCE-SCAN.md` section 2, "Table: `artifacts`" (lines 255-265)

The scan enumerates all artifact columns: `sha256`, `media_type`, `size_bytes`, `filename`, `storage_uri`, `storage_class`, `created_by`, `reference_count`, `created_at`. No `entity_type`. No `metadata` JSONB.

**Verdict for H5.3:** CONFIRMED (no entity_type, no metadata JSONB, SHA-256 PK)

#### H5.4: API Router Count
**Source:** `BACKEND-SOURCE-SCAN.md` section 1.5 (lines 57-71) and section 6 router list (lines 476-488)

Section 1.5 table enumerates 12 router files:
`agent.py`, `artifacts.py`, `auth.py`, `conversations.py`, `health.py`, `manifests.py`, `pointers.py`, `rag.py`, `runs.py`, `sessions.py`, `streams.py`, `tags.py`

Section 6 router composition also lists 12 paths: `/health`, `/auth`, `/agent`, `/artifacts`, `/conversations`, `/manifests`, `/pointers`, `/rag`, `/runs`, `/sessions`, `/streams`, `/tags`.

Original H5.5 already identified this as a discrepancy (11 claimed, 12 actual). The source scan confirms: **12 routers exist**, not 11.

**Verdict for H5.4:** ORIGINAL CLAIM REFUTED — router count is 12, not 11. Tags router was added in migration 0004 but not reflected in original documentation count.

#### H5.5: Database Table Count
**Source:** `BACKEND-SOURCE-SCAN.md` section 2 (Model Registry, all `Table:` entries)

Tables enumerated by the backend scan:

| Group | Tables |
|-------|--------|
| auth.py | `tenants`, `users`, `api_keys` |
| conversations.py | `sessions`, `conversations`, `messages`, `message_feedback` |
| rag.py | `rag_chunks` |
| runs.py | `runs`, `run_events` |
| substrate.py | `artifacts`, `manifests`, `pointers`, `pointer_history` |
| tags.py | `tags` |
| **Total** | **15 tables** |

Grep confirmation: The pattern `Table: \`` appears exactly 15 times in BACKEND-SOURCE-SCAN.md (lines 167, 177, 189, 204, 221, 233, 246, 255, 267, 278, 290, 299, 312, 323, 336).

**The documented "16 tables" claim is incorrect — the actual count is 15.**

**Verdict for H5.5:** ORIGINAL CLAIM REFUTED — 15 tables, not 16. The discrepancy likely arose from an off-by-one error in original counting. No missing table has been found.

### H5 Overall Verdict: PARTIALLY CONFIRMED

**Confirmed:** Enum members, graph architecture, artifact schema, ChatOpenAI-only LLM, SSE via PG LISTEN/NOTIFY, 4 migrations.

**Refuted:**
- Router count: 12 (not 11) — `tags` router undercounted
- Table count: 15 (not 16) — overcounted by one in original documentation

**Confidence:** HIGH
**Severity:** LOW — these count discrepancies do not affect architectural understanding.

**Action Items:**
- Update PLATFORM-GROUND-TRUTH.md: "11 routers" → "12 routers"
- Update PLATFORM-GROUND-TRUTH.md: "16 tables" → "15 tables"
- Correct MEMORY.md claim: "16 tables, 11 API routers" → "15 tables, 12 API routers"

---

## H6: Migration State Accuracy

### Original Claim
Exactly 4 migrations exist as documented with specific file names and table creations.

### Source Code Evidence
**Source:** `BACKEND-SOURCE-SCAN.md` section 9 (Code Metrics) and section 10 (Gap Identification)

The backend scan at section 10 states:
> `db/checkpointer.py` — LangGraph checkpointer (psycopg pool)

And section 7 (Configuration) confirms `checkpointer_pool_size: int = 5`.

The backend scan does not re-enumerate migration files directly, but:
- It confirms 15 tables total (consistent with 4 migrations creating them)
- Section 10 confirms all tables are "Fully Implemented"
- Migration 0004 is confirmed as adding `sessions`, `conversations`, `messages`, `message_feedback`, `tags` (referenced in H5.4 and the tag router)
- The LangGraph checkpointer uses psycopg pool (not part of Alembic migrations, a separate checkpointer schema)

The original H6 evidence cited specific file listing:
```
20260123_0001_initial_substrate.py
20260123_0002_auth_tables.py
20260124_0003_rag_chunks.py
20260201_0004_conversations_sessions_tags.py
```

This is consistent with the backend scan's model registry which accounts for all 15 tables across exactly these 4 logical groups.

**Note on LangGraph Checkpointer:** The LangGraph psycopg checkpointer likely creates its own checkpoint tables at runtime (standard LangGraph behavior). These are not SQLAlchemy Alembic migrations and are NOT included in the 15-table count. This is consistent — the 15 tables are application tables only.

### H6 Verdict: CONFIRMED

**Confidence:** HIGH
**Evidence Quality:** Indirect (backend scan confirms table groups consistent with 4 migrations; no direct migration file re-scan was performed)

**Action Items:** None. Next migration should be 0005, split per DEC-052 into 0005a/b/c.

---

## H7: P0 Bug Accuracy

### Original Claims
Two P0 bugs:
1. Race condition in `_get_next_sequence` (runs.py, lines 366-379): TOCTOU gap between SELECT max and INSERT
2. Worker registration bug: `WorkerSettings.functions` evaluated at class definition time, before `@job()` decorators run

### Source Code Evidence

#### H7.1: Sequence Number Race Condition
**Source:** `BACKEND-SOURCE-SCAN.md` section 1.6 (repositories/) and section 9 (Code Metrics)

The backend scan at section 1.6 confirms `repositories/runs.py` exists with method `get_next_sequence()` listed as a key method of `MessageRepository` (messages.py). The runs repository key methods include `create_run()`, `start()`, `pause()`, `resume()`, `complete()` — the `_get_next_sequence` is an internal helper not listed in section 1.6 but is consistent with the `run_events` table having a `sequence_num` column (confirmed in section 2, `run_events` table, line 319: "sequence_num (Int)").

The `run_events` table schema (BACKEND-SOURCE-SCAN.md line 319) shows `sequence_num` is a plain `Int` with no `GENERATED ALWAYS AS IDENTITY` or `DEFAULT nextval(...)` notation — confirming the application-level sequence generation rather than database-level, which is the root cause of the race condition.

**Verdict for H7.1:** CONFIRMED (sequence_num is application-managed Int; no database-level uniqueness protection found in scan)

#### H7.2: Worker Registration Bug
**Source:** `BACKEND-SOURCE-SCAN.md` section 1.1 (`core/jobs.py`)

The backend scan lists `core/jobs.py` as "(partial scan)" with key class `JobQueue`. The scan did not enumerate the full class definition, but confirms the file exists and serves arq integration.

The original H7 evidence (hypotheis-code-alignment.md lines 265-299) provides the actual code showing:
- `_job_registry = {}` initialized at module level (line 21)
- `WorkerSettings.functions = list(_job_registry.values())` evaluated at class definition (line 277)
- `@job("parse_document")` decorator runs after `WorkerSettings` is defined (line 190+)

The backend scan at section 10 marks Jobs/Scheduling as:
> `⚠️ Jobs/Scheduling — core/jobs.py (arq integration) not scanned in detail`

This partial scan status means we cannot confirm bug resolution from the scan alone. The bug evidence comes from the original H7 hypothesis document's direct code citation, which remains the authoritative source. The backend scan does not contradict it.

**Verdict for H7.2:** CONFIRMED (bug evidence from direct code citation in original H7; backend scan does not contradict; arq file exists with status "not scanned in detail", no evidence of fix)

### H7 Overall Verdict: CONFIRMED — both bugs remain documented as unresolved

**Confidence:** HIGH for H7.1 (schema confirms application-managed sequence_num); MEDIUM for H7.2 (arq file not fully scanned in v2 evidence)

**Action Items:**
- INFRA-BUG-001 (sequence race): Fix `_get_next_sequence` — use `GENERATED ALWAYS AS IDENTITY` on `sequence_num` or `SELECT FOR UPDATE` with serializable isolation
- INFRA-BUG-002 (worker init): Fix `WorkerSettings.functions` — use `@staticmethod` or `@classmethod` returning `list(_job_registry.values())` at runtime, or defer module loading
- Both bugs are production-blocking and should remain in backlog with HIGH priority

---

## H8: Docker Compose Redis Profile

### Original Claim
Redis service in docker-compose.yml has `profiles: ["full"]`.

### Source Code Evidence
**Source:** `BACKEND-SOURCE-SCAN.md` section 7 (Configuration) references docker-compose indirectly; original H8 directly cited docker-compose.yml lines 55-64.

The backend scan at section 7 confirms:
- Redis is referenced via `core/cache.py` (listed in section 1.1: "In-memory caching")
- `core/jobs.py` includes `WorkerSettings.redis_settings()` static method (cited in original H7 evidence)
- The `mcp_transport` setting supports "streamable-http" — no Redis dependency for MCP

The backend scan does not re-scan docker-compose.yml, but the configuration system (section 7) shows no Redis URL in `Settings` — consistent with Redis being optional (profile-gated), not required.

The original H8 code citation showed:
```yaml
redis:
  image: redis:7-alpine
  profiles:
    - full
```

With additional profiles: `observability` for Langfuse. This multi-profile structure is consistent with the backend scan's partial implementations (`⚠️ Cache Layer — core/cache.py not scanned in detail`).

### H8 Verdict: CONFIRMED

**Confidence:** HIGH (original code citation directly; scan is consistent with optional Redis)
**Action Items:** None.

---

## Summary Table (H5–H8)

| Hypothesis | Original Verdict | v2 Verdict | Change | Key Finding |
|---|---|---|---|---|
| **H5.1** RunEventType enum (28 members) | CONFIRMED | CONFIRMED | None | 28 members, APPROVAL_* all present |
| **H5.2** LangGraph 3-node graph | CONFIRMED | CONFIRMED | Clarification | Nodes are agent/tools/capture_sources; backend scan section 5 imprecisely lists END instead of capture_sources |
| **H5.3** Artifact schema (no entity_type/metadata) | CONFIRMED | CONFIRMED | None | SHA-256 PK, 8 columns, no entity_type, no metadata |
| **H5.4** 11 API routers | Minor Discrepancy | REFUTED | Upgraded severity | 12 routers confirmed (tags undercounted in docs) |
| **H5.5** 16 database tables | Not explicitly tested | REFUTED | NEW FINDING | 15 tables confirmed (overcounted by 1 in docs) |
| **H6** 4 migrations, next is 0005 | CONFIRMED | CONFIRMED | None | 4 migrations consistent with 15 tables across 4 groups |
| **H7.1** Sequence race condition | CONFIRMED | CONFIRMED | None | `sequence_num` is plain Int, application-managed — TOCTOU gap confirmed |
| **H7.2** Worker init bug | CONFIRMED | CONFIRMED | Confidence downgrade | MEDIUM confidence (arq file "not scanned in detail" in v2 source) |
| **H8** Redis profile "full" | CONFIRMED | CONFIRMED | None | Cache layer exists; Redis is optional (profile-gated) |

---

## New Hypotheses from Source Code vs Documentation Gaps

### H9: Frontend Pointer Type Schema Mismatch

**Discovery Source:** `FRONTEND-SOURCE-SCAN.md` section 5 (lines 426-438) vs `BACKEND-SOURCE-SCAN.md` section 2 (lines 278-288)

**Hypothesis:** The frontend TypeScript `Pointer` interface includes fields not present in the backend SQLAlchemy model, indicating either stale frontend types or a planned schema extension not yet applied.

**Evidence:**

Frontend `types/api.ts` defines:
```typescript
type PointerType = 'bundle' | 'corpus' | 'snapshot'

interface Pointer {
  pointer_type: PointerType   // NOT in backend model
  description?: string | null  // NOT in backend model
  metadata: Record<string, unknown>  // NOT in backend model
  ...
}
```

Backend `pointers` table schema (BACKEND-SOURCE-SCAN.md lines 278-288) columns:
`id`, `tenant_id`, `namespace`, `name`, `manifest_sha256`, `status`, `published_manifest_sha256`, `created_by`, `updated_by`, `created_at`, `updated_at`

No `pointer_type`, no `description`, no `metadata` column in the database model.

**Implication:** If the frontend `PointerViewer.tsx` renders `pointer_type`, `description`, or `metadata`, those fields will always be undefined at runtime. The frontend type was likely written ahead of the database schema, or reflects a design intent not yet migrated.

**Verdict:** SCHEMA MISMATCH — frontend types do not match backend model
**Confidence:** HIGH
**Severity:** MEDIUM — runtime silent nulls in PointerViewer; no crash but fields never render
**Action Items:**
- Add migration 0005b (per DEC-052) to add `pointer_type`, `description`, `metadata JSONB` columns to `pointers` table
- OR strip these fields from frontend types if they were speculative
- Update PointerResponse Pydantic schema to match DB model

---

### H10: Frontend Run Type Schema Extended Beyond Backend

**Discovery Source:** `FRONTEND-SOURCE-SCAN.md` section 5 (lines 441-464) vs `BACKEND-SOURCE-SCAN.md` section 2 (lines 299-310)

**Hypothesis:** Frontend `Run` TypeScript interface includes fields not present in the backend `runs` table, suggesting frontend was developed ahead of schema.

**Evidence:**

Frontend `types/api.ts` `Run` interface includes:
```typescript
token_usage: Record<string, unknown>  // Not in backend runs table
cost_cents: number                     // Not in backend runs table (backend uses cost_micros)
project_id?: string | null            // Not in backend runs table
session_id?: string | null            // Not in backend runs table (indirect via config only)
parent_run_id?: string | null         // Not in backend runs table
```

Backend `runs` table (BACKEND-SOURCE-SCAN.md lines 300-310):
`id`, `run_type`, `name`, `status`, `started_at`, `completed_at`, `input_manifest_sha256`, `output_manifest_sha256`, `config`, `result`, `error`, `created_at`

No `token_usage`, no `cost_cents`, no `project_id`, no `session_id`, no `parent_run_id`.

**Note on cost:** Backend uses `cost_micros` (confirmed in conversations model at line 230), but frontend uses `cost_cents` — different unit and different table.

**Verdict:** SCHEMA MISMATCH — frontend Run type has 5 fields not in backend schema
**Confidence:** HIGH
**Severity:** HIGH — `session_id` linkage (frontend assumes run-session FK, but no such column exists in `runs` table); cost unit mismatch could cause calculation errors
**Action Items:**
- Reconcile Run schema: decide which fields to add to `runs` table in migration 0005
- Align cost unit: pick `cost_micros` (backend convention) or `cost_cents` (frontend convention)
- Add `token_usage` JSONB, `session_id` FK, `parent_run_id` FK to runs table if needed

---

### H11: `capture_sources` Node is Undocumented in Backend Scan Section 5

**Discovery Source:** `BACKEND-SOURCE-SCAN.md` section 5 (lines 448-466) vs original H5.2 evidence (hypothesis-code-alignment.md lines 58-90)

**Hypothesis:** The backend scan's section 5 summary of the LangGraph graph incorrectly omits the `capture_sources` node, which is the third real node implementing source citation capture. This creates a documentation-within-scan discrepancy that could mislead future readers of the scan.

**Evidence:**

Backend scan section 5 lists graph nodes as:
1. Agent Node
2. ToolNode
3. END (listed as a "node")

Original H5.2 (from direct code at research_assistant.py lines 159-183) shows:
```python
graph.add_node("agent", self._agent_node)
graph.add_node("tools", ToolNode(self.tools))
graph.add_node("capture_sources", self._capture_sources_node)
graph.add_edge("tools", "capture_sources")
graph.add_edge("capture_sources", "agent")
```

`capture_sources` is a real node that executes `_capture_sources_node` (a method) and forms a loop back to `agent`. END is not a node — it is a terminal sentinel. The backend scan summary (section 5) got the third node wrong.

**Verdict:** SCAN INACCURACY — BACKEND-SOURCE-SCAN.md section 5 incorrectly describes the graph
**Confidence:** HIGH (direct code citation in original hypothesis is unambiguous)
**Severity:** MEDIUM — could mislead developers about graph structure (source capture is critical for citation system)
**Action Items:**
- Correct BACKEND-SOURCE-SCAN.md section 5: replace "3. END — Conversation termination" with "3. capture_sources — Extracts cited sources from tool results, loops back to agent"
- Note that `_capture_sources_node` feeds the `sources` list in `ResearchState`, which is consumed by `useThreadSources()` hook on the frontend

---

### H12: Superagent Orchestration Model Has No Parity Mapping

**Discovery Source:** `01-extracts/orchestration-extract.md` (lines 1-100) vs `BACKEND-SOURCE-SCAN.md` sections 1.8 and 5

**Hypothesis:** The Superagent PlanSet/Plan/PlanTask orchestration hierarchy (from production analysis) has no corresponding data model in the NYQST backend, meaning parity work has not yet started on multi-plan orchestration.

**Evidence:**

Orchestration extract (lines 1-100) defines:
- `PlanSet` — root execution context (chat_id, workspace_id, Dict[plan_id, Plan])
- `Plan` — phase with tasks in LinkedList order (previous_plan_id), used_sources
- `PlanTask` — individual task with start/end timing, notes, entities, sources

NYQST backend has:
- `runs` table: `run_type`, `config` JSONB, `input_manifest_sha256`, `output_manifest_sha256`
- `run_events` table: append-only ledger with `event_type`, `payload` JSONB
- `ResearchAssistantGraph`: 3-node StateGraph with `ResearchState` (messages, context_pointer_id, manifest_sha256, sources, error, run_id)

There is no `PlanSet`, no `Plan`, no `PlanTask` — no multi-phase planning hierarchy. The NYQST graph runs as a single stateful loop (agent → tools → capture_sources → agent) with no concept of "research phases" or "adaptive re-planning".

**Implication:** Superagent's streaming event `task_update` (which carries a full `plan_set` object) has no backend equivalent. The NYQST `run_events` ledger could theoretically represent task phases as events, but this mapping has not been designed.

**Verdict:** PARITY GAP CONFIRMED — multi-phase orchestration (PlanSet → Plan → PlanTask) is entirely absent from NYQST
**Confidence:** HIGH
**Severity:** HIGH — this is a core Superagent capability that directly affects the Research Module's ability to show planning progress in the UI
**Action Items:**
- Design decision needed: implement PlanSet/Plan/PlanTask as JSONB within run_events payloads, or as new tables in migration 0005c
- Streaming events `task_update` and `update_subagent_current_action` need NYQST equivalents mapped to `RunEventType` enum members (`STEP_STARTED`, `STEP_COMPLETED` are partial candidates)
- This is a Wave 1 implementation item; confirm placement in IMPLEMENTATION-PLAN.md

---

### H13: Superagent Streaming Event Taxonomy Has No NYQST Mapping

**Discovery Source:** `01-extracts/streaming-events-extract.md` (lines 1-100) vs `BACKEND-SOURCE-SCAN.md` section 6 (streams router)

**Hypothesis:** The 22 Superagent production streaming events (NDJSON over SSE) have fundamentally different semantics from NYQST's RunEventType enum (28 members, PostgreSQL LISTEN/NOTIFY), requiring an explicit mapping or translation layer.

**Evidence:**

Superagent streaming events (from streaming-events-extract.md lines 19-44):
- Planning events: `task_update`, `pending_sources`
- Tool events: `node_tools_execution_start`, `node_tool_event`, `update_subagent_current_action`
- Report events: `node_report_preview_start`, `node_report_preview_delta`, `node_report_preview_done`
- Browser events: `browser_use_start`, `browser_use_stop`, `browser_use_await_user_input`
- Clarification events: `clarification_needed`, `update_message_clarification_message`

NYQST RunEventType (from H5 evidence, runs.py lines 30-53):
- Lifecycle: `RUN_STARTED`, `RUN_PAUSED`, `RUN_RESUMED`, `RUN_COMPLETED`, `RUN_FAILED`, `RUN_CANCELLED`
- Steps: `STEP_STARTED`, `STEP_COMPLETED`
- Tool: `TOOL_CALL_STARTED`, `TOOL_CALL_COMPLETED`
- LLM: `LLM_REQUEST`, `LLM_RESPONSE`
- Retrieval: `RETRIEVAL_QUERY`, `RETRIEVAL_RESULT`
- Artifacts: `ARTIFACT_EMITTED`, `MANIFEST_CREATED`, `POINTER_MOVED`
- State: `CHECKPOINT`, `STATE_UPDATE`
- Human: `USER_INPUT`, `APPROVAL_REQUESTED`, `APPROVAL_GRANTED`, `APPROVAL_DENIED`, `COMMENT_ADDED`
- Error: `ERROR`, `WARNING`

Key gaps:
- No NYQST equivalent for `task_update` (planning phase progress)
- No NYQST equivalent for `node_report_preview_*` (streaming report generation)
- No NYQST equivalent for `browser_use_*` (browser automation)
- No NYQST equivalent for `clarification_needed` (human-in-loop clarification)
- `message_delta` (Superagent) maps to LangGraph token streaming, not a RunEventType

Additionally, NYQST SSE transport uses PG LISTEN/NOTIFY (`BACKEND-SOURCE-SCAN.md` line 70: "SSE endpoints (run events via PG LISTEN/NOTIFY, activity feed)") while Superagent uses NDJSON push. The protocols are different.

NYQST frontend `useSSE` hook (FRONTEND-SOURCE-SCAN.md section 4, lines 337-354) consumes NYQST SSE events, not Superagent NDJSON.

**Verdict:** STRUCTURAL GAP — Superagent and NYQST event taxonomies are distinct; 7+ Superagent event categories have no NYQST equivalent
**Confidence:** HIGH
**Severity:** HIGH — implementing Superagent parity requires either extending RunEventType or designing a separate streaming layer
**Action Items:**
- Add to DECISION-REGISTER: decide whether to extend `RunEventType` with planning/report/browser events or introduce a parallel event channel
- GML/report streaming (`node_report_preview_*`) is the highest-priority gap (affects Research Module output)
- `clarification_needed` maps to `APPROVAL_REQUESTED` only loosely; formal mapping needed for HitL workflows

---

## Final Confidence Summary

| Hypothesis | Verdict | Confidence | Severity |
|---|---|---|---|
| H5 (Ground Truth overall) | PARTIALLY CONFIRMED | HIGH | LOW |
| H5 router count (11→12) | REFUTED | HIGH | LOW |
| H5 table count (16→15) | REFUTED | HIGH | LOW |
| H6 (4 migrations) | CONFIRMED | HIGH | N/A |
| H7.1 (sequence race) | CONFIRMED | HIGH | CRITICAL |
| H7.2 (worker init bug) | CONFIRMED | MEDIUM | CRITICAL |
| H8 (Redis profile) | CONFIRMED | HIGH | N/A |
| H9 (Pointer schema mismatch) | NEW — SCHEMA MISMATCH | HIGH | MEDIUM |
| H10 (Run schema mismatch) | NEW — SCHEMA MISMATCH | HIGH | HIGH |
| H11 (capture_sources omitted in scan) | NEW — SCAN INACCURACY | HIGH | MEDIUM |
| H12 (PlanSet/Plan/PlanTask absent) | NEW — PARITY GAP | HIGH | HIGH |
| H13 (Event taxonomy mismatch) | NEW — STRUCTURAL GAP | HIGH | HIGH |

---

## Consolidated Action Items

### Immediate Documentation Fixes
1. **MEMORY.md:** Update "16 tables, 11 API routers" → "15 tables, 12 API routers"
2. **PLATFORM-GROUND-TRUTH.md:** Update router count to 12, table count to 15
3. **BACKEND-SOURCE-SCAN.md section 5:** Correct graph node 3 from "END" to "capture_sources"

### Schema Alignment (Migration 0005)
4. **Pointer table:** Add `pointer_type`, `description`, `metadata JSONB` columns (or strip from frontend types)
5. **Runs table:** Add `token_usage JSONB`, `session_id FK`, `parent_run_id FK`; align cost unit (micros vs cents)

### Bug Tracking (already in backlog, no change needed)
6. **INFRA-BUG-001:** RunEvent sequence race condition — remains unresolved
7. **INFRA-BUG-002:** WorkerSettings init order bug — remains unresolved

### Architecture Decisions Needed
8. **PlanSet/Plan/PlanTask:** Decide implementation approach for multi-phase orchestration
9. **Event taxonomy bridge:** Decide how Superagent streaming events map to NYQST RunEventType enum
10. **Report streaming:** Design `node_report_preview_*` equivalent for NYQST (GML pipeline, per DEC-043/DEC-015b)
