# [GAP-008] CONSISTENCY-AUDIT-PLANS Part 3 identifies seven stale claims (SC-01 through SC-07) in planning documents that have not been corrected. The most impactful: (a) IMPLEMENTATION-PLAN "What We Get For Free" table lists arq background jobs as "Available" when the worker process operational status is unverified; (b) GIT-ISSUES BL-016 claims "arq + Redis already configured" implying it works; (c) DECISION-REGISTER DEC-040 says GML healer is Python/Pydantic when the frontend healer is TypeScript/HAST.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-008
- **Severity**: MEDIUM
- **Description**: CONSISTENCY-AUDIT-PLANS Part 3 identifies seven stale claims (SC-01 through SC-07) in planning documents that have not been corrected. The most impactful: (a) IMPLEMENTATION-PLAN "What We Get For Free" table lists arq background jobs as "Available" when the worker process operational status is unverified; (b) GIT-ISSUES BL-016 claims "arq + Redis already configured" implying it works; (c) DECISION-REGISTER DEC-040 says GML healer is Python/Pydantic when the frontend healer is TypeScript/HAST.
- **Affected BL Items**: BL-016 (entity substrate uses arq), BL-004/BL-009 (GML healer)
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS SC-01 through SC-07
- **Resolution**: Apply all seven corrections listed in CONSISTENCY-AUDIT-PLANS SC-01 through SC-07. Specifically: downgrade arq status to "unverified"; add arq operational verification to Phase 0 checklist; split DEC-040 into DEC-040a (backend Python healer) and DEC-040b (frontend TypeScript/HAST healer).
- **Owner Recommendation**: Documentation lead; review each SC item and apply correction
- **Wave**: P0

---

### GAP-009 — Dependency Graph Errors in GIT-ISSUES (8 Blocked-By Fields Wrong)