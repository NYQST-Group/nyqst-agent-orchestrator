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

## References
- BACKLOG.md: BL-001
- IMPLEMENTATION-PLAN.md: Sections 1.1, 1.2

---