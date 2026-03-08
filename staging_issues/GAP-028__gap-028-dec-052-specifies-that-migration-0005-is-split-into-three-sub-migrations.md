# [GAP-028] DEC-052 specifies that Migration 0005 is split into three sub-migrations: 0005a (DB schema changes), 0005b (LangGraph state extensions), 0005c (indices). The split is decided but the content of each sub-migration is not specified anywhere. Multiple backlog items depend on Migration 0005 (BL-005, BL-006, BL-012, BL-016, BL-018 per GAP-009). Without a specification of what tables/columns/indices are in each sub-migration, there is a risk of merge conflicts and ordering issues during implementation.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-028
- **Severity**: MEDIUM
- **Description**: DEC-052 specifies that Migration 0005 is split into three sub-migrations: 0005a (DB schema changes), 0005b (LangGraph state extensions), 0005c (indices). The split is decided but the content of each sub-migration is not specified anywhere. Multiple backlog items depend on Migration 0005 (BL-005, BL-006, BL-012, BL-016, BL-018 per GAP-009). Without a specification of what tables/columns/indices are in each sub-migration, there is a risk of merge conflicts and ordering issues during implementation.
- **Affected BL Items**: BL-005, BL-006, BL-012, BL-016, BL-018
- **Source Evidence**: DEC-052; CONSISTENCY-AUDIT-PLANS I-05, I-06, I-07
- **Resolution**: Document MIG-0005A/b/c content: (a) 0005a: subscriptions table, usage_records table, entity_type column on relevant tables, tags schema extensions; (b) 0005b: RunState extensions (planning_hierarchy fields, cost accumulator fields); (c) 0005c: indices for entity lookup, usage aggregation, run timeline queries.
- **Owner Recommendation**: Backend architecture lead
- **Wave**: W0 — prerequisite for multiple BL items

---

### GAP-029 — Billing Port from DocuIntelli Not Verified