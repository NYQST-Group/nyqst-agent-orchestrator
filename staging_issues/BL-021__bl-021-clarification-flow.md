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

## Policy Evaluation Algorithm (GAP-084)

BL-021 implements graph interrupts, but the trigger policy determines **when** to interrupt. Four interrupt policy templates govern this:

| Policy Template | Interrupt Behaviour | Use Case |
|---|---|---|
| **Exploratory** | No interrupts at all. Run proceeds without any pause/resume | Open-ended research where user wants minimal friction |
| **Standard** | Interrupt only for `approval_required` tool categories (e.g., tools that make external API calls costing money or that write data) | Default policy for most research runs |
| **Regulated** | Interrupt before any external data access (before any tool that reaches outside the platform — web, API, document retrieval) | Compliance-sensitive workflows |
| **Audit-Critical** | Interrupt at every plan step (before each PlanTask is dispatched via Send()) | Full human oversight mode |

**Policy evaluation algorithm** (in `planner_node` or a policy guard before `fan_out`):

```python
def should_interrupt(policy: str, context: dict) -> bool:
    """
    Called before each tool dispatch or plan step.
    Returns True if execution should pause for human approval.
    """
    if policy == "exploratory":
        return False

    if policy == "standard":
        # Interrupt only if the tool category is in the approval_required set
        return context.get("tool_category") in APPROVAL_REQUIRED_CATEGORIES

    if policy == "regulated":
        # Interrupt before any external data access
        return context.get("accesses_external_data", False)

    if policy == "audit_critical":
        # Interrupt at every plan step
        return context.get("is_plan_step", False)

    return False  # Default: no interrupt

APPROVAL_REQUIRED_CATEGORIES = {
    "financial_data_purchase",   # Paid API data (FactSet, Bloomberg)
    "external_write",            # Any write operation to external system
    "web_scrape_volume",         # High-volume scraping (>10 URLs per task)
}
```

**Storage**: Policy template stored on the `Run` record as `interrupt_policy: str` (default: "standard"). Set at run creation time from the `deliverable_type` or explicit user selection.

**LangGraph implementation**: Use `interrupt_before=["research_worker_node"]` (audit_critical) or custom interrupt edges with `should_interrupt()` checks embedded in the conditional routing logic.

## References
- BACKLOG.md: BL-021
- IMPLEMENTATION-PLAN.md: Section 3.9
- docs/adr/009-human-in-the-loop-governance.md (ADR-009)
- GAP-084 (policy evaluation specification)

---