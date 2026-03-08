# [GAP-005] ADR-004 specifies the Index Service Architecture (contract-first, pluggable backends: OpenSearch + pgvector). The KNOWLEDGE-MAP confirms it is a key platform component. However, the IMPLEMENTATION-PLAN's "ten platform primitives" list does not include the Index Service. It is documented in the ADR and referenced in PLATFORM-FRAMING.md, but a developer building the primitives would not know it belongs at Layer 1 from reading the IMPLEMENTATION-PLAN alone.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-005
- **Severity**: HIGH
- **Description**: ADR-004 specifies the Index Service Architecture (contract-first, pluggable backends: OpenSearch + pgvector). The KNOWLEDGE-MAP confirms it is a key platform component. However, the IMPLEMENTATION-PLAN's "ten platform primitives" list does not include the Index Service. It is documented in the ADR and referenced in PLATFORM-FRAMING.md, but a developer building the primitives would not know it belongs at Layer 1 from reading the IMPLEMENTATION-PLAN alone.
- **Affected BL Items**: BL-003 (web research MCP tools), BL-016 (entity/citation substrate)
- **Source Evidence**: hypothesis-consistency.md H1 gap 3; KNOWLEDGE-MAP Section 3 (Infrastructure & Storage)
- **Resolution**: Add "Index Service (pluggable search backend)" as the eleventh platform primitive in IMPLEMENTATION-PLAN, or add a footnote under the existing "MCP Tool Layer" primitive that explicitly calls out Index Service as a sub-component. Cross-reference ADR-004.
- **Owner Recommendation**: Architecture lead
- **Wave**: W0 — before BL-003 or BL-016 implementation

---

### GAP-006 — Document Processing Pipeline Strategy Not in Decision Register