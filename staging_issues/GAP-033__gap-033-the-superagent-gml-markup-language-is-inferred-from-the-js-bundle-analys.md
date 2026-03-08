# [GAP-033] The Superagent GML markup language is inferred from the JS bundle analysis. The EXTRACTION-SUMMARY and orchestration-extract.md document 17–18 GML tags with high confidence. However, the formal schema — the exact rules for which tags can nest inside which, the full attribute set for `gml-chartcontainer` props, the complete `gml-infoblockmetric` schema, and the healer's nesting rules — is inferred from code, not documented from a formal spec (which is not publicly available). The NYQST implementation must be compatible with Superagent's output but cannot verify compatibility without the formal spec.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-033
- **Severity**: HIGH
- **Description**: The Superagent GML markup language is inferred from the JS bundle analysis. The EXTRACTION-SUMMARY and orchestration-extract.md document 17–18 GML tags with high confidence. However, the formal schema — the exact rules for which tags can nest inside which, the full attribute set for `gml-chartcontainer` props, the complete `gml-infoblockmetric` schema, and the healer's nesting rules — is inferred from code, not documented from a formal spec (which is not publicly available). The NYQST implementation must be compatible with Superagent's output but cannot verify compatibility without the formal spec.
- **Affected BL Items**: BL-004 (Markup AST schema), BL-009 (ReportRenderer)
- **Source Evidence**: EXTRACTION-SUMMARY (GML inferred from 344 KB bundle); orchestration-extract.md Section 3.1 (healer rules inferred)
- **Resolution**: Accept the inference approach as sufficient for v1 (the 18 tags and nesting rules are extracted at HIGH confidence). Document the inference confidence in the NDM v1 schema spec (GAP-017). Plan a validation step in Phase 2: generate a report using the NYQST system, compare its GML structure to a Superagent reference report, and adjust nesting rules if needed. This is acceptable risk.
- **Owner Recommendation**: Architecture lead — risk acceptance decision
- **Wave**: W2 — validation step post-implementation

---

### GAP-034 — Superagent Authentication Method Unknown