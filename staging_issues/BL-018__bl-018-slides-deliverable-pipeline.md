# [BL-018] Slides Deliverable Pipeline
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:medium`, `track:deliverables`, `size:M`
**Milestone:** M2: Deliverables
**Blocked By:** BL-001, MIG-0005A
**Blocks:** None

**Body:**
## Overview
Create a slides generation pipeline producing a reveal.js HTML bundle from research results. 4-stage process: outline, per-slide content, assembly, and artifact storage. Output is a single HTML file artifact viewable in an iframe.

## Acceptance Criteria
- [ ] 4-stage pipeline: outline -> per-slide content -> reveal.js assembly -> artifact storage
- [ ] Output stored as single Artifact with entity_type=GENERATED_PRESENTATION
- [ ] Artifact content is valid reveal.js HTML
- [ ] AI message hydrated_content includes gml-ViewSlides (or gml-ViewWebsite -- decide before implementation)
- [ ] `GET /api/v1/artifacts/{sha256}/content` returns the HTML

## Technical Notes
- Net-new file: `src/intelli/agents/graphs/nodes/slides_generation.py`
- AD-3 decision: reveal.js HTML format (consistent with web artifact pattern)
- Single HTML file artifact (not multi-file Manifest)
- See IMPLEMENTATION-PLAN.md Section 2.4

## References
- BACKLOG.md: BL-018
- IMPLEMENTATION-PLAN.md: Section 2.4

---