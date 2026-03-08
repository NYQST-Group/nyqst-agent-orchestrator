# [GAP-010] BL-015 (DeliverableStore Zustand slice) and BL-008 (DeliverableSelector component) have no dependencies and can start in Week 1 (Wave 0). Both are currently assigned to `phase:3-frontend` and Milestone M3 in GIT-ISSUES — an artifact of "all frontend in Phase 3" waterfall thinking. This means frontend work that unblocks other items is scheduled 8–10 weeks later than it needs to be.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-010
- **Severity**: MEDIUM
- **Description**: BL-015 (DeliverableStore Zustand slice) and BL-008 (DeliverableSelector component) have no dependencies and can start in Week 1 (Wave 0). Both are currently assigned to `phase:3-frontend` and Milestone M3 in GIT-ISSUES — an artifact of "all frontend in Phase 3" waterfall thinking. This means frontend work that unblocks other items is scheduled 8–10 weeks later than it needs to be.
- **Affected BL Items**: BL-015, BL-008
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-09, 2B
- **Resolution**: Update GIT-ISSUES BL-015 and BL-008: change phase label to `phase:0-foundation`, update milestone to M0. No code change required.
- **Owner Recommendation**: Project coordinator
- **Wave**: P0

---

### GAP-011 — IMPLEMENTATION-PLAN Critical Path Arrow Backwards for BL-022