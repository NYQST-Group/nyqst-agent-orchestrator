# [GAP-017] The KNOWLEDGE-MAP Section 10 explicitly lists "NDM v1 exact JSON schema (sketched in SUPERAGENT_PARITY_PLAN §3.4, needs formalization)" as a needed-soon open thread. The orchestration-extract.md specifies the DataBrief schema (BL-022) but the NDM (NYQST Document Markup) v1 schema — the JSON AST format used for report generation (DEC-015a) — is only sketched. BL-004 (Markup AST schema) depends on this being locked before implementation.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-017
- **Severity**: HIGH
- **Description**: The KNOWLEDGE-MAP Section 10 explicitly lists "NDM v1 exact JSON schema (sketched in SUPERAGENT_PARITY_PLAN §3.4, needs formalization)" as a needed-soon open thread. The orchestration-extract.md specifies the DataBrief schema (BL-022) but the NDM (NYQST Document Markup) v1 schema — the JSON AST format used for report generation (DEC-015a) — is only sketched. BL-004 (Markup AST schema) depends on this being locked before implementation.
- **Affected BL Items**: BL-004, BL-005 (report generation pipeline), BL-009 (ReportRenderer)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; DEC-015a; BL-004 in BACKLOG.md
- **Resolution**: Formalize the NDM v1 JSON schema as a standalone specification document. Required fields: node types (18 GML tags mapped to JSON node representations), nesting rules, chart data structure, citation reference format, section hierarchy. This is a prerequisite for BL-004.
- **Owner Recommendation**: Architecture lead — can be derived from GML-RENDERING-ANALYSIS tag inventory and orchestration-extract.md Section 3.1
- **Wave**: W0 — blocks BL-004

---

### GAP-018 — MCP Tool Discovery Filtering Algorithm Unspecified