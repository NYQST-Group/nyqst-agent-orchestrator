# [GAP-004] The PRD (03_PLATFORM.md) specifies six integrated modules: Research, Document Management, Analysis (infinite canvas), Modelling (provable methods), Knowledge & Domain, and Organisational Insight. The IMPLEMENTATION-PLAN v3 frames work as "ten platform primitives" validated through the Research Module. The Analysis Module (infinite canvas for visual analysis) does not appear anywhere in BL-001 through BL-022. There is no explicit statement in the IMPLEMENTATION-PLAN that the Analysis Module is deferred and why. A product manager or new team member reading both documents cannot determine the deferred scope without cross-referencing all six modules against the backlog.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-004
- **Severity**: HIGH
- **Description**: The PRD (03_PLATFORM.md) specifies six integrated modules: Research, Document Management, Analysis (infinite canvas), Modelling (provable methods), Knowledge & Domain, and Organisational Insight. The IMPLEMENTATION-PLAN v3 frames work as "ten platform primitives" validated through the Research Module. The Analysis Module (infinite canvas for visual analysis) does not appear anywhere in BL-001 through BL-022. There is no explicit statement in the IMPLEMENTATION-PLAN that the Analysis Module is deferred and why. A product manager or new team member reading both documents cannot determine the deferred scope without cross-referencing all six modules against the backlog.
- **Affected BL Items**: None in current backlog (the gap IS the absence of any BL item)
- **Source Evidence**: hypothesis-consistency.md H1 gap 1; KNOWLEDGE-MAP Section 2 (Platform Layer)
- **Resolution**: Add a "Deferred Scope" section to IMPLEMENTATION-PLAN explicitly listing the three deferred PRD modules (Analysis, Modelling, Organisational Insight) with rationale and the ADR/DEC that defers them. This does not require new decisions — it is a documentation clarification.
- **Owner Recommendation**: Product lead; 1-hour documentation task
- **Wave**: W0 — before Phase 1 design reviews

---

### GAP-005 — Index Service Not Listed as Layer 1 Primitive