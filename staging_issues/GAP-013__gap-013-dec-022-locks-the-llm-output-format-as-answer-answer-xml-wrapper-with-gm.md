# [GAP-013] DEC-022 locks the LLM output format as `<answer>...</answer>` XML wrapper with `<gml-*>` tags inside. GML-RENDERING-ANALYSIS (which specifies the complete GML rendering pipeline) does not mention the `<answer>` wrapper at all. There is no specification for where and how the wrapper is stripped before the GML content reaches the renderer.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-013
- **Severity**: LOW
- **Description**: DEC-022 locks the LLM output format as `<answer>...</answer>` XML wrapper with `<gml-*>` tags inside. GML-RENDERING-ANALYSIS (which specifies the complete GML rendering pipeline) does not mention the `<answer>` wrapper at all. There is no specification for where and how the wrapper is stripped before the GML content reaches the renderer.
- **Affected BL Items**: BL-009 (ReportRenderer)
- **Source Evidence**: CONSISTENCY-AUDIT-ANALYSIS C-09; CONSISTENCY-AUDIT-PLANS SC-03 (partial)
- **Resolution**: Add a "Pre-processing Step" to GML-RENDERING-ANALYSIS Section 7 (Implementation Checklist): "1. Extract GML content from `<answer>...</answer>` wrapper before passing to GmlRenderer. Handle: partial `<answer>` during streaming (buffer until closing tag), malformed wrapper (fallback to plain markdown rendering), nested tags inside the answer body."
- **Owner Recommendation**: Frontend track lead; update GML-RENDERING-ANALYSIS only
- **Wave**: W0 — before BL-009 implementation

---

## Category 2: Design Gaps

### GAP-014 — No Explicit Integration Contract for LangGraph → SSE Pipeline