# ADR-009: Human-in-the-Loop and Governance Patterns

**Status:** Proposed
**Date:** 2026-01-26
**Deciders:** Mark Forster, Engineering Team
**PRD Reference:** [06_ARCHITECTURE.md - Human-in-the-Loop Patterns](../prd/06_ARCHITECTURE.md), [03_PLATFORM.md - Governance](../prd/03_PLATFORM.md)

---

## Context

NYQST is built on the premise that trust is architectural, not cosmetic. The platform must support humans inspecting, approving, overriding, and guiding agent work. This requires:

1. **Interrupt and resume**: Agents must be able to pause at defined points and wait for human input before continuing.
2. **Approval gates**: Certain actions (pointer promotion, external writes, schema changes) require human approval based on the configured "level of care."
3. **Trust escalation**: As confidence in agent outputs grows, humans can reduce oversight. As risk increases, more gates are required.
4. **State inspection**: When an agent pauses, humans must be able to see the full context — what the agent did, what it proposes to do, what evidence supports the proposal.
5. **Feedback capture**: Human approvals, rejections, and modifications must be recorded in the run ledger for learning and audit.
6. **Policy-driven**: The level of human involvement is configurable per project, module, or workflow — not hard-coded.

Today's codebase has:
- Run ledger supports `human.approval.recorded` and `human.comment.added` event types
- LangGraph (in dependencies) provides `interrupt_before` / `interrupt_after` patterns for human-in-the-loop
- No policy engine implementation
- No approval workflow UI components (though `ApprovalPanel` exists in the component library as a placeholder)
- Reference Design §2.7 specifies Decision objects for approvals and sign-offs

---

## Decision

Adopt a **policy-driven governance model** with three layers: interrupt patterns (LangGraph), approval workflows (platform), and trust levels (policy configuration).

### Governance Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Trust Levels (Policy Configuration)           │
│  ─────────────────────────────────────────────          │
│  Policy templates define required gates per action type  │
│  e.g., "regulated" requires approval for all promotions  │
│        "standard" requires approval for external writes  │
│        "exploratory" requires no approvals               │
└──────────────────────┬──────────────────────────────────┘
                       │ configures
┌──────────────────────▼──────────────────────────────────┐
│  Layer 2: Approval Workflows (Platform)                  │
│  ─────────────────────────────────────────────          │
│  ApprovalRequest → human review → Decision record       │
│  Recorded in run ledger with full context                │
└──────────────────────┬──────────────────────────────────┘
                       │ uses
┌──────────────────────▼──────────────────────────────────┐
│  Layer 1: Interrupt Patterns (LangGraph)                 │
│  ─────────────────────────────────────────────          │
│  interrupt_before / interrupt_after on graph nodes       │
│  Agent pauses, UI shows approval panel, agent resumes    │
└─────────────────────────────────────────────────────────┘
```

### Trust Level Policies

```python
PolicyTemplate(
    name: str,                    # "exploratory" | "standard" | "regulated" | "audit_critical"
    description: str,

    gates: list[GateRule],
)

GateRule(
    action: str,                  # Action that triggers the gate
    gate_type: str,               # "approve" | "review" | "notify" | "auto"
    required_role: str | None,    # Minimum role to approve (e.g., "admin", "reviewer")
    timeout_action: str,          # What happens if no response: "block" | "auto_approve" | "escalate"
    timeout_hours: int,
)
```

**Predefined Policy Templates:**

| Template | Description | Gate Rules |
|----------|-------------|------------|
| **exploratory** | Unrestricted agent work. Suitable for research, brainstorming, internal exploration. | No gates. All actions auto-approved. |
| **standard** | Default for most work. Approvals for external writes and promotions. | `pointer.promote` → approve, `connector.*.write` → approve, `claim.decide` → review |
| **regulated** | High-care workflows. Approvals for most state changes. | All promotions → approve, all external writes → approve, schema changes → approve, claim decisions → approve |
| **audit_critical** | Maximum oversight. Every significant action requires approval. | All pointer moves → approve, all external actions → approve, all claims → approve, model changes → approve |

### Gate Actions

| Action Pattern | Description |
|---------------|-------------|
| `substrate.pointer.advance` | Moving a pointer to a new manifest |
| `substrate.pointer.promote` | Promoting a bundle to a corpus (governance gate) |
| `connector.*.write` | Any write to an external system (Slack, HubSpot, etc.) |
| `claim.create` | Creating a formal claim (fact, interpretation, requirement) |
| `claim.decide` | Recording a decision on a claim |
| `schema.promote` | Promoting a discovered schema to a governed schema |
| `run.execute_workflow` | Starting a governed workflow |

### Approval Request Flow

```
Agent proposes action
       │
       ▼
┌──────────────────┐
│ Policy Engine     │  ← Check GateRules for this action + policy template
│ evaluates         │
└──────┬───────────┘
       │
  ┌────▼──────┐
  │ Gate       │
  │ required?  │
  └────┬──────┘
       │
  No ──┤── Yes
       │       │
       │  ┌────▼─────────────┐
       │  │ Create            │
       │  │ ApprovalRequest   │
       │  └────┬─────────────┘
       │       │
       │  ┌────▼─────────────┐
       │  │ LangGraph         │
       │  │ interrupt_before  │  ← Agent pauses execution
       │  └────┬─────────────┘
       │       │
       │  ┌────▼─────────────┐
       │  │ UI shows          │  ← ApprovalPanel with full context:
       │  │ ApprovalPanel     │     what agent proposes, evidence, risks
       │  └────┬─────────────┘
       │       │
       │  ┌────▼─────────────┐
       │  │ Human decides     │  ← approve / reject / modify
       │  └────┬─────────────┘
       │       │
       │  ┌────▼─────────────┐
       │  │ Record Decision   │  ← Run ledger event:
       │  │ in Run Ledger     │     human.approval.recorded
       │  └────┬─────────────┘
       │       │
       │  ┌────▼─────────────┐
       │  │ LangGraph resumes │  ← Agent continues (or halts on rejection)
       │  └────┬─────────────┘
       │       │
       └───────┤
               ▼
       Action executed (or blocked)
```

### Approval Request Model

```python
ApprovalRequest(
    id: UUID,
    run_id: UUID,                     # Which run is requesting approval
    session_id: UUID | None,
    action: str,                      # e.g., "substrate.pointer.promote"
    gate_rule: GateRule,              # Which policy rule triggered this
    context: ApprovalContext,         # Full context for the reviewer
    status: str,                      # "pending" | "approved" | "rejected" | "expired"
    requested_at: datetime,
    decided_at: datetime | None,
    decided_by: UUID | None,         # User who decided
    decision_reason: str | None,     # Human's explanation
)

ApprovalContext(
    summary: str,                     # Agent's explanation of what it wants to do
    evidence: list[EvidenceRef],      # Supporting evidence (artifact refs, search results)
    proposed_changes: dict,           # What will change if approved
    risk_assessment: str | None,      # Agent's self-assessment of risk
    current_state: dict,              # Relevant current state for context
)
```

### Feedback Loop

Human decisions feed back into the platform:

1. **Run ledger**: Every approval/rejection recorded with full context and rationale
2. **Trust calibration**: Over time, patterns of approvals can inform policy relaxation ("this agent type's promotions are always approved → suggest auto-approve")
3. **Skill improvement**: Rejected actions with feedback inform agent prompt/skill refinement
4. **Audit trail**: Complete chain from agent proposal → human decision → outcome

---

## Options Considered

### Option 1: LangGraph Interrupts Only

**Description:** Use LangGraph's interrupt mechanism directly, with no platform-level governance layer.

**Pros:**
- Simple implementation
- Direct integration with agent runtime

**Cons:**
- No policy-driven configuration (hard-coded interrupt points)
- No structured approval records
- No trust level escalation/de-escalation
- Interrupt decisions not recorded in platform run ledger

### Option 2: External Workflow Engine (Camunda)

**Description:** Route approvals through Camunda BPMN workflows for full governance orchestration.

**Pros:**
- Enterprise-grade workflow execution
- BPMN standard for process definition
- Complex multi-step approval chains

**Cons:**
- Additional infrastructure component
- Overkill for current approval patterns
- Learning curve for BPMN
- Premature — deferral trigger not yet met

### Option 3: Policy-Driven with LangGraph Interrupts (Selected)

**Description:** Platform Policy Engine evaluates gate rules and triggers LangGraph interrupts when approval is needed. Decisions recorded in run ledger.

**Pros:**
- Policy-driven (configurable, not hard-coded)
- Uses LangGraph's proven interrupt mechanism
- Full audit trail in run ledger
- Trust levels scale from exploratory to audit-critical
- Foundation for later Camunda integration if needed

**Cons:**
- Must build Policy Engine and Approval Request system
- Simple interrupt model may not support complex multi-stage approvals
- Policy template design requires domain understanding

---

## Decision Rationale

Option 3 (Policy-Driven + LangGraph Interrupts) was chosen because:

1. **Policy-driven is core to the platform**: The Reference Design specifies "policy-driven levels of care" as a core principle. This must be configurable, not hard-coded.
2. **LangGraph interrupt is the right primitive**: The interrupt mechanism handles the hard part (agent pause/resume with state preservation). We add policy evaluation and structured record-keeping on top.
3. **Gradual trust building**: The "exploratory → standard → regulated" progression matches how organizations adopt AI systems. Start permissive, tighten as workflows mature.
4. **Audit by default**: Every decision is recorded in the run ledger with context, which is essential for compliance and learning.
5. **Camunda as upgrade path**: If approval workflows become complex (multi-stage, multi-role, conditional), Camunda can be added behind the same policy interface. The Reference Design marks Camunda as a deferral item.

---

## Consequences

### Positive

- Human oversight is configurable per project/workflow, not one-size-fits-all
- Trust builds incrementally as agents prove reliability
- Full audit trail for compliance and learning
- LangGraph handles state preservation during approval waits
- Policy templates are reusable across projects

### Negative

- Policy Engine is new infrastructure to build and maintain
- Approval UX must surface sufficient context for informed decisions
- Long-running approvals may block agent execution (mitigated by timeouts)
- Policy template design requires understanding of risk profiles

### Risks

- **Risk:** Approval fatigue — too many gates slow down work
  - **Mitigation:** Start with "standard" (minimal gates). Add gates only for high-risk actions. Policy templates are adjustable. Trust calibration can suggest reducing gates based on approval patterns.
- **Risk:** Approval context insufficient for informed decisions
  - **Mitigation:** `ApprovalContext` requires agents to provide summary, evidence, and risk assessment. UI renders these prominently. Reviewers can request more context before deciding.
- **Risk:** Long approval wait times block agent workflows
  - **Mitigation:** Configurable timeouts with escalation. For non-blocking patterns, agent can continue other work while waiting. Notifications push approval requests to reviewers.

---

## Implementation Notes

1. **Policy Engine**: Implement as `PolicyEngine` service in `src/intelli/services/governance/policy_engine.py`. Takes an action + session context, returns whether a gate is required and what type.
2. **Policy templates**: Store as JSON in the database. Seed with the four predefined templates. Allow project-level overrides.
3. **Approval Request**: New database model in `src/intelli/db/models/governance.py`. API endpoints: `POST /api/v1/approvals` (create, called by agent pipeline), `GET /api/v1/approvals` (list pending), `POST /api/v1/approvals/{id}/decide` (approve/reject).
4. **LangGraph integration**: Create a `GovernanceNode` that checks policy before executing governed actions. If a gate is required, creates an `ApprovalRequest` and triggers `interrupt_before`. On resume, checks the decision and proceeds or halts.
5. **UI integration**: The existing `ApprovalPanel` component (in `packages/ui-library`) should render `ApprovalContext` with evidence links, proposed changes, and approve/reject/modify actions. Real-time notification via SSE when approvals are pending.
6. **Run ledger events**: Emit `human.approval.requested`, `human.approval.recorded` (with decision + reason), and `agent.action.gated` events.

---

## Related ADRs

- ADR-005: Agent Runtime & Framework — LangGraph provides interrupt mechanism
- ADR-006: Session & Workspace Architecture — Policy template bound to session/project
- ADR-008: MCP Tool Architecture — Tool execution pipeline checks policy before execution

---

## References

- [PLATFORM_REFERENCE_DESIGN.md §2.7 — Evidence/Claims/Decisions](../PLATFORM_REFERENCE_DESIGN.md)
- [PLATFORM_REFERENCE_DESIGN.md §9 — Governance + Promotion](../PLATFORM_REFERENCE_DESIGN.md)
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
- [PLATFORM_FOUNDATION.md — F4: Orchestration Layer](../planning/PLATFORM_FOUNDATION.md)
