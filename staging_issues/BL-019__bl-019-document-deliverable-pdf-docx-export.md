# [BL-019] Document Deliverable (PDF/DOCX Export)
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:medium`, `track:deliverables`, `size:M`
**Milestone:** M2: Deliverables
**Blocked By:** BL-004, BL-005
**Blocks:** None

**Body:**
## Overview
Build an export pipeline that converts MarkupDocument AST to PDF (via weasyprint) and DOCX (via python-docx). Provides a new API endpoint that loads a report artifact, deserializes the MarkupDocument, renders to the requested format, stores the output as a new Artifact, and returns a download URL.

## Acceptance Criteria
- [ ] `POST /api/v1/artifacts/{sha256}/export` with `{"format": "pdf"}` returns valid PDF
- [ ] `POST /api/v1/artifacts/{sha256}/export` with `{"format": "docx"}` returns valid DOCX
- [ ] PDF preserves heading hierarchy, tables, and at least one chart rendered as image
- [ ] DOCX preserves heading hierarchy and table structure
- [ ] Output stored as new Artifact with appropriate entity_type (GENERATED_DOCUMENT)
- [ ] Response includes download URL for the generated file

## Technical Notes
- Net-new files: `src/intelli/services/export/document_export.py`, `src/intelli/services/export/markup_to_html.py`
- New endpoint in: `src/intelli/api/v1/artifacts.py`
- Pipeline: MarkupDocument -> HTML (markup_to_html) -> weasyprint -> PDF bytes
- Pipeline: MarkupDocument -> python-docx Document -> bytes
- Dependencies to add: `weasyprint>=62.0`, `python-docx>=1.1.0`
- AD-4 decision: weasyprint (server-side, CSS-driven)
- See IMPLEMENTATION-PLAN.md Section 2.5

## References
- BACKLOG.md: BL-019
- IMPLEMENTATION-PLAN.md: Section 2.5

---

### Wave 3: Depends on Wave 2 items

---