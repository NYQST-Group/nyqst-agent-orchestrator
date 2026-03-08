# [GAP-006] ADR-007 specifies a tiered document processing pipeline (Fast, Standard, Deep) with parser adapters (Docling primary, Unstructured fallback, LlamaParse optional). DECISION-REGISTER has DEC-030 (PDF export via WeasyPrint) and DEC-033 (Jina Reader API), but there is no decision capturing the tiered pipeline strategy itself. A developer implementing document ingestion would not know the three-tier approach is specified in ADR-007 or that Docling is the primary parser.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-006
- **Severity**: HIGH
- **Description**: ADR-007 specifies a tiered document processing pipeline (Fast, Standard, Deep) with parser adapters (Docling primary, Unstructured fallback, LlamaParse optional). DECISION-REGISTER has DEC-030 (PDF export via WeasyPrint) and DEC-033 (Jina Reader API), but there is no decision capturing the tiered pipeline strategy itself. A developer implementing document ingestion would not know the three-tier approach is specified in ADR-007 or that Docling is the primary parser.
- **Affected BL Items**: Any backlog items involving document ingestion or RAG (BL-016 adjacent)
- **Source Evidence**: hypothesis-consistency.md H2 gap 2 (ADR-007 partial reflection)
- **Resolution**: Add a decision to DECISION-REGISTER capturing: "Document processing: tiered pipeline (Fast/Standard/Deep tiers) using Docling 2.3+ as primary parser, Unstructured 0.15+ as fallback, LlamaParse as optional paid API. Canonical output format: DocIR artifact." Cross-reference ADR-007.
- **Owner Recommendation**: Backend track lead
- **Wave**: W0 — before any document processing implementation

---

### GAP-007 — ADR-010 Infrastructure Not in Decision Register