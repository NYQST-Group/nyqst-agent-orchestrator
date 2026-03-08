# [GAP-001] DEC-048 locks Plotly.js (`react-plotly.js`) as the chart library. This is correct and grounded in Superagent bundle analysis (Superagent uses Plotly via `gml-chartcontainer`). However, the decision has NOT been written back into four documents that still specify Recharts: IMPLEMENTATION-PLAN section 3.6, GIT-ISSUES BL-009 acceptance criteria ("CHART nodes render as Recharts charts"), STRATEGIC-REVIEW (recommended Recharts for bundle size), and the LIBRARY-REFERENCE LIB-13 section. A developer reading any of these documents will use the wrong library.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-001
- **Severity**: CRITICAL
- **Description**: DEC-048 locks Plotly.js (`react-plotly.js`) as the chart library. This is correct and grounded in Superagent bundle analysis (Superagent uses Plotly via `gml-chartcontainer`). However, the decision has NOT been written back into four documents that still specify Recharts: IMPLEMENTATION-PLAN section 3.6, GIT-ISSUES BL-009 acceptance criteria ("CHART nodes render as Recharts charts"), STRATEGIC-REVIEW (recommended Recharts for bundle size), and the LIBRARY-REFERENCE LIB-13 section. A developer reading any of these documents will use the wrong library.
- **Affected BL Items**: BL-004, BL-005, BL-009, BL-019
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-01, I-14; hypothesis-consistency.md H1; EXTRACTION-SUMMARY confirms Plotly in Superagent bundle
- **Resolution**: Update IMPLEMENTATION-PLAN section 3.6 to "Chart rendering: react-plotly.js". Update GIT-ISSUES BL-009 acceptance criteria to Plotly. Update STRATEGIC-REVIEW to reflect DEC-048. Confirm LIB-13 in LIBRARY-REFERENCE documents `react-plotly.js`. Mark I-01 and I-14 as resolved.
- **Owner Recommendation**: Documentation lead / plan owner; 30-minute task per document
- **Wave**: P0 — must complete before any implementation code is written

---

### GAP-002 — GML Rendering Pipeline Split Not Propagated