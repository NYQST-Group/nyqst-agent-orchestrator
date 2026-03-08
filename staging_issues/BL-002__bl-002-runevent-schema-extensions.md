# [BL-002] RunEvent Schema Extensions
**Labels:** `type:infrastructure`, `phase:0-foundation`, `priority:critical-path`, `track:infrastructure`, `size:S`
**Milestone:** M0: Foundation
**Blocked By:** None
**Blocks:** BL-001, BL-007, BL-014, BL-016, BL-020, BL-021

**Body:**
## Overview
Extend the existing RunEvent type enum with 19 new event types covering planning, subagent fan-out, streaming content, artifacts, clarification, report generation progress, and web research events. This is the foundational schema change that all orchestrator and frontend work depends on.

## Acceptance Criteria
- [ ] All 19 new event types added to `RunEventType` enum in both `schemas/runs.py` and `db/models/runs.py`
- [ ] Typed `log_*` helper methods added to `LedgerService` for each new event type, following existing `async def log_*(self, run_id, ...) -> RunEvent` pattern
- [ ] All new event types round-trip through the ledger (create, read back)
- [ ] New events appear correctly in the SSE stream via PG LISTEN/NOTIFY
- [ ] Existing event types and all existing tests remain unaffected
- [ ] Payload shapes documented as Python TypedDict or Pydantic models

## Technical Notes
- Existing types to keep: STATE_UPDATE, TOOL_CALL_*, STEP_*
- New types: PLAN_CREATED, PLAN_TASK_STARTED, PLAN_TASK_COMPLETED, PLAN_TASK_FAILED, SUBAGENT_DISPATCHED, SUBAGENT_COMPLETED, SUBAGENT_FAILED, CONTENT_DELTA, ARTIFACT_CREATED, CLARIFICATION_NEEDED, CLARIFICATION_RECEIVED, REPORT_PREVIEW_START, REPORT_PREVIEW_DELTA, REPORT_PREVIEW_DONE, WEB_SEARCH_STARTED, WEB_SEARCH_COMPLETED, WEB_SCRAPE_STARTED, WEB_SCRAPE_COMPLETED, REFERENCES_FOUND
- Files to modify: `src/intelli/schemas/runs.py`, `src/intelli/db/models/runs.py`, `src/intelli/services/runs/ledger_service.py`
- See IMPLEMENTATION-PLAN.md Section 0.2 for full payload schemas

## References
- BACKLOG.md: BL-002
- IMPLEMENTATION-PLAN.md: Section 0.2

---