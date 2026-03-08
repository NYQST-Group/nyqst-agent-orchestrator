# [BL-017] Meta-Reasoning Node
**Labels:** `type:feature`, `phase:1-orchestrator`, `priority:high`, `track:orchestrator`, `size:M`
**Milestone:** M1: Orchestrator
**Blocked By:** BL-001
**Blocks:** None

**Body:**
## Overview
Add a meta-reasoning node to the orchestrator graph that evaluates research quality after fan-in. Identifies data gaps, failed tasks, and incomplete coverage, then dispatches targeted recovery tasks. Adds 30-60s latency but dramatically improves output quality. Includes a skip heuristic for simple queries.

## Acceptance Criteria
- [ ] Meta-reasoning LLM call evaluates TaskResults against original plan
- [ ] Identifies three categories: data gaps, failed tasks, incomplete coverage
- [ ] When gaps found: dispatches recovery tasks via same Send() pattern
- [ ] When no gaps: routes directly to synthesis node
- [ ] Skip heuristic: bypasses for `len(plan) <= 2` or explicit config flag
- [ ] STATE_UPDATE event emitted with quality assessment payload
- [ ] Latency overhead logged (target: < 30s for meta-reasoning LLM call)

## Technical Notes
- Extends: `src/intelli/agents/graphs/research_assistant.py` (new node in graph)
- Recovery dispatch reuses research_worker_node
- Prompt pattern: system prompt evaluates plan vs results, returns JSON list of follow-up tasks (empty = no gaps)
- `state["meta_reasoning_done"]` prevents infinite loops
- See IMPLEMENTATION-PLAN.md Section 1.4 for prompt template

## References
- BACKLOG.md: BL-017
- IMPLEMENTATION-PLAN.md: Section 1.4

---