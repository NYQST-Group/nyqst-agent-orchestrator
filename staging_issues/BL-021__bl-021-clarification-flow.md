# [BL-021] Clarification Flow
**Labels:** `type:feature`, `phase:3-frontend`, `priority:medium`, `track:orchestrator`, `size:M`
**Milestone:** M3: Frontend
**Blocked By:** BL-001, BL-002
**Blocks:** None

**Body:**
## Overview
Implement mid-run pause/resume via CLARIFICATION_NEEDED events. When the planner detects an ambiguous query, it emits the event, pauses the graph (checkpointed via existing AsyncPostgresSaver), and waits for user input. The ClarificationPrompt component renders in the chat UI, and POST /api/v1/runs/{run_id}/clarify resumes the graph from checkpoint.

## Acceptance Criteria
- [ ] Ambiguous query triggers CLARIFICATION_NEEDED event with question and context payload
- [ ] Run status set to PAUSED; graph checkpointed via AsyncPostgresSaver
- [ ] `POST /api/v1/runs/{run_id}/clarify` accepts answer, logs CLARIFICATION_RECEIVED, resumes graph
- [ ] ClarificationPrompt.tsx appears in chat UI when CLARIFICATION_NEEDED received on active run SSE
- [ ] After answer submitted, run resumes from checkpoint and completes normally
- [ ] `message.needs_clarification_message` populated on pause, cleared on resume

## Technical Notes
- Server side: conditional route after planner_node; reuse existing AsyncPostgresSaver from db/checkpointer.py
- Client side: net-new `ui/src/components/chat/ClarificationPrompt.tsx`
- New endpoint: `POST /api/v1/runs/{run_id}/clarify` in runs.py
- CLARIFICATION_NEEDED and CLARIFICATION_RECEIVED already in BL-002 event types
- Note: full UI may slip to v1.5 per BACKLOG.md tradeoff log, but schema is ready
- See IMPLEMENTATION-PLAN.md Section 3.9

## References
- BACKLOG.md: BL-021
- IMPLEMENTATION-PLAN.md: Section 3.9

---