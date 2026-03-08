# [BL-022] Shared Data Brief
**Labels:** `type:feature`, `phase:1-orchestrator`, `priority:high`, `track:orchestrator`, `size:S`
**Milestone:** M1: Orchestrator
**Blocked By:** None (design phase)
**Blocks:** None

**Body:**
## Overview
Design and implement the shared data brief -- a structured intermediate representation produced by the synthesis node that all downstream generators reference for data consistency. This is a LangGraph state field, not a new table. The brief ensures 100% data consistency (same numbers across all deliverable files), mirroring Superagent's pattern.

> **Note:** DataBrief schema design must precede BL-001 (feeds into ResearchState). Integration testing requires BL-001.

## Acceptance Criteria
- [ ] DataBrief shape defined: key_facts, entities (name/type/value/source_url), financial_figures (label/value/unit/source_url), summary
- [ ] DataBrief populated by synthesis_node from aggregated TaskResults
- [ ] DataBrief appears in final graph state after a test run
- [ ] Downstream deliverable nodes receive DataBrief via state (not re-fetched)
- [ ] Existing graph tests unaffected

## Technical Notes
- DataBrief is a dict in `ResearchState.data_brief` (LangGraph state field)
- Option (a) chosen: state carries it naturally, no new table or artifact needed
- Synthesis node uses LLM to extract structured facts from raw TaskResults
- See IMPLEMENTATION-PLAN.md Section 1.1 for DataBrief shape

## References
- BACKLOG.md: BL-022
- IMPLEMENTATION-PLAN.md: Section 1.1

---