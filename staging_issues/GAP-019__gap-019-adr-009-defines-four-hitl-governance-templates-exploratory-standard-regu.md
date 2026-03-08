# [GAP-019] ADR-009 defines four HITL governance templates (Exploratory, Standard, Regulated, Audit-Critical). KNOWLEDGE-MAP Section 10 lists "Policy evaluation order (ADR-009 lists 4 templates, needs conflict resolution)" as an open thread. When a run is configured with a governance template, the exact precedence rules for when to interrupt vs. continue are not specified. DEC-047 defers the clarification UI to v1.5 but the backend schema and interrupt logic are in scope for v1.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-019
- **Severity**: MEDIUM
- **Description**: ADR-009 defines four HITL governance templates (Exploratory, Standard, Regulated, Audit-Critical). KNOWLEDGE-MAP Section 10 lists "Policy evaluation order (ADR-009 lists 4 templates, needs conflict resolution)" as an open thread. When a run is configured with a governance template, the exact precedence rules for when to interrupt vs. continue are not specified. DEC-047 defers the clarification UI to v1.5 but the backend schema and interrupt logic are in scope for v1.
- **Affected BL Items**: BL-021 (clarification flow — backend schema)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; ADR-009; DEC-047
- **Resolution**: Document the policy evaluation algorithm for the four templates: Exploratory (no interrupts); Standard (interrupt on approval_required tool categories); Regulated (interrupt before any external data access); Audit-Critical (interrupt at every plan step). This specification belongs in BL-021 technical notes and is a prerequisite for the LangGraph interrupt implementation.
- **Owner Recommendation**: Product lead + backend architecture lead
- **Wave**: W1 — before BL-021 implementation

---

### GAP-020 — Entity Reference Algorithm Edge Cases Unspecified