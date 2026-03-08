# [BL-004] NYQST Markup AST Schema
**Labels:** `type:infrastructure`, `phase:0-foundation`, `priority:critical-path`, `track:deliverables`, `size:M`
**Milestone:** M0: Foundation
**Blocked By:** None
**Blocks:** BL-005, BL-009, BL-019

**Body:**
## Overview
Create the Pydantic model definitions for the NYQST Markup AST -- a document tree with 18 node types that represents structured reports. This is the intermediate representation between LLM output and rendered deliverables. Includes a MarkupHealer that auto-repairs invalid trees.

## Acceptance Criteria
- [ ] `MarkupNodeType` enum with all 18 node types (document, section, columns, column, heading, paragraph, blockquote, table, table_row, table_cell, chart, image, list, list_item, code_block, inline, metric_card, callout)
- [ ] `MarkupNode` model with type, attrs, children, text, and citation_ids fields
- [ ] `MarkupDocument` model with version, title, nodes, and metadata
- [ ] `MarkupHealer.heal()` coerces unknown node types to PARAGRAPH
- [ ] `MarkupHealer.validate()` returns list of validation warnings
- [ ] Round-trip `JSON -> MarkupDocument -> JSON` is stable (idempotent)
- [ ] `MarkupDocument.model_validate(json)` works for all 18 node types

## Technical Notes
- Net-new file: `src/intelli/schemas/markup.py`
- Chart node attrs: chart_type, data, config
- Heading node attrs: level (1-6)
- Inline node attrs: bold, italic, code, href, citation_id
- Metric_card node attrs: label, value, delta, trend
- Callout node attrs: type (info/warn/error/success)
- See IMPLEMENTATION-PLAN.md Section 0.3 for full schema

## References
- BACKLOG.md: BL-004
- IMPLEMENTATION-PLAN.md: Section 0.3

---