# [GAP-002] DEC-015 was split into DEC-015a (backend MarkupDocument JSON AST, used by BL-004/BL-005 report generation) and DEC-015b (frontend GML rendering uses rehype-to-JSX, NOT a JSON AST intermediate layer). This split resolves the conflict between DEC-015 and GML-RENDERING-ANALYSIS. However, multiple documents still reference the old undivided DEC-015 and the conflict is still listed as open. CONSISTENCY-AUDIT-ANALYSIS Section 5.3 flagged this as the "most significant unresolved conflict in the entire document set." GML-RENDERING-ANALYSIS's Section 4 recommendation (skip JSON AST, use rehype-to-JSX) is NOW CORRECT under DEC-015b, but the document doesn't know this because DEC-015 was not split when GML-RENDERING-ANALYSIS was written.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-002
- **Severity**: CRITICAL
- **Description**: DEC-015 was split into DEC-015a (backend MarkupDocument JSON AST, used by BL-004/BL-005 report generation) and DEC-015b (frontend GML rendering uses rehype-to-JSX, NOT a JSON AST intermediate layer). This split resolves the conflict between DEC-015 and GML-RENDERING-ANALYSIS. However, multiple documents still reference the old undivided DEC-015 and the conflict is still listed as open. CONSISTENCY-AUDIT-ANALYSIS Section 5.3 flagged this as the "most significant unresolved conflict in the entire document set." GML-RENDERING-ANALYSIS's Section 4 recommendation (skip JSON AST, use rehype-to-JSX) is NOW CORRECT under DEC-015b, but the document doesn't know this because DEC-015 was not split when GML-RENDERING-ANALYSIS was written.
- **Affected BL Items**: BL-004, BL-005, BL-009 (report generation and rendering pipeline)
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS SC-02, I-13; CONSISTENCY-AUDIT-ANALYSIS C-04, C-11; hypothesis-consistency.md H3 gap 2
- **Resolution**: Add a "Status Update" note to GML-RENDERING-ANALYSIS Section 4 clarifying that the DEC-015 split has resolved the conflict — its rehype-to-JSX recommendation is confirmed as DEC-015b. Update DEC-015 entry in DECISION-REGISTER to show the split clearly. Update any document that cross-references DEC-015 to distinguish the two sub-decisions.
- **Owner Recommendation**: Architecture lead; requires 1–2 hours to update all cross-references
- **Wave**: P0 — required before BL-004 or BL-009 implementation begins

---

### GAP-003 — Open Questions Still Appear Open in Source Documents