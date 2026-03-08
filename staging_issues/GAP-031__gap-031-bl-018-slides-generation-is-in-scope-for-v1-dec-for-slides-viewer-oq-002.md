# [GAP-031] BL-018 (Slides Generation) is in scope for v1. DEC for slides viewer (OQ-002 resolution) specifies: reuse iframe approach, `gml-viewpresentation` renders a link card in Phase 1/2, embedded reveal.js deferred to Phase 3. The slides generation pipeline (7 stages documented in orchestration-extract.md Section 3.3 for website) is documented for websites, but the slides-specific pipeline is not documented. The DataBrief-to-slides transformation logic and the GML tag set for presentations (`gml-viewpresentation`) are not specified.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-031
- **Severity**: LOW
- **Description**: BL-018 (Slides Generation) is in scope for v1. DEC for slides viewer (OQ-002 resolution) specifies: reuse iframe approach, `gml-viewpresentation` renders a link card in Phase 1/2, embedded reveal.js deferred to Phase 3. The slides generation pipeline (7 stages documented in orchestration-extract.md Section 3.3 for website) is documented for websites, but the slides-specific pipeline is not documented. The DataBrief-to-slides transformation logic and the GML tag set for presentations (`gml-viewpresentation`) are not specified.
- **Affected BL Items**: BL-018 (Slides Generation)
- **Source Evidence**: orchestration-extract.md Section 3.3 (website 7 stages); DEC-043 (OQ-002 resolution); KNOWLEDGE-MAP Section 5 (Document Generation Contract)
- **Resolution**: Add slides-specific pipeline specification to BL-018 technical notes. Minimally: (1) DataBrief → slides generator LLM prompt template; (2) Output format: series of `<gml-viewpresentation>` sections with section slides; (3) Viewer: link card with download option for v1; (4) Streaming: `node_report_preview_start/delta/done` events reused with `deliverable_type: slides`.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1 — before BL-018 implementation

---

### GAP-032 — Clarification Flow Resume Endpoint Not Specified