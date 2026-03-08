# [GAP-021] The streaming-events-extract.md documents the connection lifecycle and retry strategy (exponential backoff, 5 attempts). The orchestration-extract.md documents the graceful degradation hierarchy (tool error → task error → plan error → run error). However, there is no document that enumerates what happens at each failure level from the platform's perspective: what state is written to the DB, what SSE events are emitted, what the user sees, and how the run is marked in the Run ledger. The "what happens if ALL fallback tools fail" case (orchestration-extract.md Section 6, open question 9) is still open.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-021
- **Severity**: MEDIUM
- **Description**: The streaming-events-extract.md documents the connection lifecycle and retry strategy (exponential backoff, 5 attempts). The orchestration-extract.md documents the graceful degradation hierarchy (tool error → task error → plan error → run error). However, there is no document that enumerates what happens at each failure level from the platform's perspective: what state is written to the DB, what SSE events are emitted, what the user sees, and how the run is marked in the Run ledger. The "what happens if ALL fallback tools fail" case (orchestration-extract.md Section 6, open question 9) is still open.
- **Affected BL Items**: BL-001 (orchestrator), BL-002 (RunEvent schema)
- **Source Evidence**: orchestration-extract.md Section 4, Section 6 open question 9; streaming-events-extract.md SSE Protocol Details
- **Resolution**: Create a failure mode table in BL-001 technical notes with four rows (tool failure, task failure, plan failure, run failure), specifying: DB state written, SSE events emitted, user-visible message, run ledger status. Define the "all fallbacks exhausted" behavior: emit `node_tool_event(event="all_tools_failed")`, mark task as failed, trigger meta-reasoning if at least 50% of other tasks succeeded, else emit plan error.
- **Owner Recommendation**: Backend architecture lead
- **Wave**: W0

---

### GAP-022 — P0 Bug: RunEvent Sequence Number Race Condition