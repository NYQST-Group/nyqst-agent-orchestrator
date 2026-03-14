# [BL-001] Research Orchestrator Graph
**Labels:** `type:feature`, `phase:1-orchestrator`, `priority:critical-path`, `track:orchestrator`, `size:XL`
**Milestone:** M1: Orchestrator
**Blocked By:** BL-002
**Blocks:** BL-003, BL-005, BL-006, BL-017, BL-018, BL-021, BL-022

**Body:**
## Overview
Extend the existing ResearchAssistantGraph (not replace it) with a planner node, Send() fan-out to parallel research workers, fan-in aggregation, synthesis node, and deliverable router. This transforms the current single-agent loop into a multi-workstream orchestrator that mirrors Superagent's 13+ parallel task pattern. The existing agent/tools/capture_sources loop is preserved and wrapped by the new research_worker_node.

## Acceptance Criteria
- [ ] Planner node decomposes query into 3-13 ResearchTask dicts and emits PLAN_CREATED event
- [ ] Fan-out dispatches Send() per task, each creating a child Run with parent_run_id FK
- [ ] Research workers execute in parallel using existing agent+tools loop
- [ ] Fan-in node aggregates all TaskResult dicts
- [ ] Synthesis node produces structured DataBrief in graph state
- [ ] Deliverable router routes by deliverable_type to appropriate generation node
- [ ] SSE stream shows: PLAN_CREATED, N x SUBAGENT_DISPATCHED, N x PLAN_TASK_*, STATE_UPDATE, CHECKPOINT
- [ ] AI message hydrated_content contains `<gml-View*>` components
- [ ] Failed tasks emit PLAN_TASK_FAILED without crashing the run
- [ ] All existing graph tests continue to pass

## Technical Notes
- Extends: `src/intelli/agents/graphs/research_assistant.py`
- Existing graph: agent -> (tools_condition) -> tools -> capture_sources -> agent (loop)
- New nodes: planner_node, fan_out, research_worker_node, fan_in_node, synthesis_node, deliverable_router
- Entry point: modify existing `POST /api/v1/agent/chat` or add `POST /api/v1/runs/research`
- research_worker_node creates child Run via `Run(parent_run_id=state["run_id"])` -- self-referential FK
- LLM system prompt must enforce `<answer>...</answer>` wrapping with `<gml-*>` component refs
- See IMPLEMENTATION-PLAN.md Section 1.2 for full graph diagram

### Sub-Issues

#### [BL-001a] ResearchState Extension
**Labels:** `type:infrastructure`, `phase:1-orchestrator`, `priority:critical-path`, `track:orchestrator`, `size:S`
- Extend ResearchState dataclass with: query, deliverable_type, plan, task_results, data_brief, web_sources, meta_reasoning_done, clarification_pending, output_artifact_sha256, child_run_ids
- All new fields must have defaults (backward-compatible)

#### [BL-001b] Planner Node
**Labels:** `type:feature`, `phase:1-orchestrator`, `priority:critical-path`, `track:orchestrator`, `size:M`
- LLM call to decompose query + deliverable_type into ResearchTask list
- Emit PLAN_CREATED event via LedgerService
- System prompt for structured JSON output of task decomposition

#### [BL-001c] Fan-Out / Fan-In Infrastructure
**Labels:** `type:feature`, `phase:1-orchestrator`, `priority:critical-path`, `track:orchestrator`, `size:L`
- Fan-out: returns `[Send("research_worker_node", {...}) for t in plan]`
- Research worker node: wraps existing agent+tools loop, creates child Run with parent_run_id
- Fan-in: accumulates TaskResult dicts, emits SUBAGENT_COMPLETED per task
- Handle per-node async DB session lifecycle (no shared session across parallel nodes)

#### [BL-001d] Synthesis Node and Deliverable Router
**Labels:** `type:feature`, `phase:1-orchestrator`, `priority:critical-path`, `track:orchestrator`, `size:M`
- Synthesis: LLM call to produce DataBrief from all TaskResults
- Deliverable router: conditional edge routing by state["deliverable_type"]
- Wire to placeholder nodes for report/website/slides/document (implemented in Phase 2)

#### [BL-001e] Integration Tests and Event Verification
**Labels:** `type:test`, `phase:1-orchestrator`, `priority:high`, `track:orchestrator`, `size:M`
- End-to-end test with real LLM: submit query, verify full event sequence in SSE
- Verify DataBrief populated in final state
- Verify child Run records have correct parent_run_id
- Contract test: ResearchState backward-compat with existing tests

## Fallback Chain Algorithm (GAP-080)

When a worker node tool fails, the following fallback chain must execute:

1. **Attempt primary provider**: dispatch tool call to primary provider (e.g., Brave for web search); emit `node_tool_event(event="tool_called")`
2. **On primary failure**: emit `node_tool_event(event="fallback_used", metadata={"failed_provider": "<name>", "trying": "<secondary>"})` and try secondary provider
3. **Try secondary provider**: if secondary also fails, continue to next fallback in the chain
4. **All fallbacks exhausted**: emit `node_tool_event(event="all_tools_failed", metadata={"task_id": "<id>", "tools_tried": [...]})` and mark task as partial (not failed)
5. **Fan-in handles partial tasks**: fan-in_node detects `has_partial_results: true` in TaskResult and routes to meta-reasoning if ≥50% of other tasks succeeded; otherwise emits plan error

Fallback chains by tool category:
- Web search: Brave → Tavily → skip (return empty results)
- Document retrieval: Jina Reader → direct fetch → skip
- Financial data: configured connector → skip

## Tool Discovery Algorithm (GAP-083)

Tool discovery runs at session creation and again at task dispatch:

1. **Session-level registration** (on session creation): register available MCP tools based on tenant tier
   - Sandbox tier: web search, document tools, basic data tools
   - Professional tier: full tool set including financial data connectors
   - Read from `tenant.features` JSONB (DEC-056)
2. **Task-level filtering** (on PlanTask creation): filter the registered tool list by task category:
   - `financial_data` tasks → financial data connector chain (FactSet-compatible API → fallback)
   - `web_search` tasks → Brave/Tavily MCP tools
   - `document` tasks → DocIR tools (file parsing, RAG query)
   - `synthesis` tasks → no external tools (LLM-only node)
3. **Pass filtered tool list** to `research_worker_node` via Send() state payload as `available_tools: list[str]`

Tool registry lives in `src/intelli/mcp/tools/` — each tool registered as MCP resource per ADR-008.

## Failure Mode Table (GAP-086)

| Failure Level | DB State Written | SSE Events Emitted | User-Visible Message | Run Ledger Status |
|---|---|---|---|---|
| **Tool failure** | `RunEvent(type=TOOL_FAILED, payload={tool_id, error, task_id})` | `node_tool_event(event="tool_called")` + `node_tool_event(event="fallback_used")` | None (silent; fallback proceeds) | Run continues |
| **Task failure** (all tools exhausted) | `RunEvent(type=TASK_FAILED, payload={task_id, tools_tried, partial_result})` | `node_tool_event(event="all_tools_failed")` + `task_update(status="error", key=task_id)` | None during streaming; shown in timeline | Task marked FAILED in PlanSet |
| **Plan failure** (<50% tasks succeeded) | `RunEvent(type=RUN_FAILED, payload={reason="insufficient_task_results", partial_tasks: N, total_tasks: M})` | `ERROR(error_type="plan_degraded")` + `done` | "Research partially failed — fewer sources than expected." | `RunStatus.FAILED` |
| **Run failure** (graph exception) | `RunEvent(type=RUN_FAILED, payload={exception_type, traceback_hash})` | `ERROR(error_type="system_error")` + `done` | "Research failed due to a system error. Please retry." | `RunStatus.FAILED` |

**"All fallbacks exhausted" behaviour**:
- Emit `node_tool_event(event="all_tools_failed")` for the affected task
- Mark task as partial in TaskResult (`partial: true, reason: "all_tools_failed"`)
- Fan-in proceeds: if ≥50% of tasks have non-partial results, trigger meta-reasoning node (BL-017) to compensate for missing data
- If <50% tasks succeeded: skip meta-reasoning, emit plan error, set `RunStatus.FAILED`

## References
- BACKLOG.md: BL-001
- IMPLEMENTATION-PLAN.md: Sections 1.1, 1.2
- docs/EVENT-CONTRACT-V1.md (SSE event types)
- GAP-080 (fallback chain), GAP-083 (tool discovery), GAP-086 (failure modes)

---