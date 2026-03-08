# [BL-009] ReportRenderer Component
**Labels:** `type:frontend`, `phase:3-frontend`, `priority:critical-path`, `track:frontend`, `size:L`
**Milestone:** M3: Frontend
**Blocked By:** BL-004, BL-005
**Blocks:** None

**Body:**
## Overview
Build a recursive React renderer that transforms MarkupDocument JSON into React elements for all 18 node types. Triggered by `<gml-ViewReport>` tags in AI message hydrated_content. Includes a GmlComponentParser that walks hydrated_content, extracts `<gml-*>` tags, and renders the appropriate React component.

## Acceptance Criteria
- [ ] All 18 MarkupNodeType values render without errors
- [ ] CHART nodes render as Recharts charts (bar, line, pie, etc.)
- [ ] METRIC_CARD nodes render as styled KPI cards with label, value, delta, trend
- [ ] TABLE nodes render as structured HTML tables
- [ ] Citation numbers render as inline superscripts using existing CitationLink.tsx
- [ ] Unknown node types fall back gracefully (render as paragraph)
- [ ] GmlComponentParser extracts `<gml-ViewReport>` from hydrated_content and launches ReportRenderer
- [ ] Data fetched from `GET /api/v1/artifacts/{sha256}/content`

## Technical Notes
- Net-new files: `ui/src/components/reports/ReportRenderer.tsx`, `ui/src/types/markup.ts`, `ui/src/components/chat/GmlComponentParser.tsx`
- Chart rendering: recharts (add to package.json if absent)
- Code blocks: react-syntax-highlighter (add if absent)
- Citations: extend existing CitationLink.tsx, do not replace
- See IMPLEMENTATION-PLAN.md Section 3.6 for TypeScript types

## References
- BACKLOG.md: BL-009
- IMPLEMENTATION-PLAN.md: Section 3.6

---