# [GAP-011] IMPLEMENTATION-PLAN dependency graph shows `BL-022 (Data Brief, design only) ◄─ BL-001`, placing BL-022 as downstream of BL-001. DEPENDENCY-ANALYSIS explicitly corrects this: the DataBrief schema design (BL-022) must precede BL-001 because BL-001 (Research Orchestrator) requires the DataBrief state field definitions to be locked first. The arrow is directionally wrong, and the critical path description `BL-002 → BL-001 → BL-022 → ...` is incorrect.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-011
- **Severity**: MEDIUM
- **Description**: IMPLEMENTATION-PLAN dependency graph shows `BL-022 (Data Brief, design only) ◄─ BL-001`, placing BL-022 as downstream of BL-001. DEPENDENCY-ANALYSIS explicitly corrects this: the DataBrief schema design (BL-022) must precede BL-001 because BL-001 (Research Orchestrator) requires the DataBrief state field definitions to be locked first. The arrow is directionally wrong, and the critical path description `BL-002 → BL-001 → BL-022 → ...` is incorrect.
- **Affected BL Items**: BL-001, BL-022
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-10, SC-04
- **Resolution**: Update IMPLEMENTATION-PLAN dependency diagram: flip `BL-022 ◄─ BL-001` to `BL-022d → BL-001`. Update critical path text to show `BL-022 (design) → BL-001 → ...`.
- **Owner Recommendation**: Architecture lead; 15-minute documentation edit
- **Wave**: P0

---

### GAP-012 — Router Count Discrepancy in PLATFORM-GROUND-TRUTH