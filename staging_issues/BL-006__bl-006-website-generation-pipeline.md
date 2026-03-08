# [BL-006] Website Generation Pipeline
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:high`, `track:deliverables`, `size:L`
**Milestone:** M2: Deliverables
**Blocked By:** BL-001, MIG-0005A
**Blocks:** BL-010

**Body:**
## Overview
Create a 7-stage website generation pipeline as a LangGraph node. Produces a multi-file website bundle (HTML/CSS/JS) stored as a Manifest of Artifacts. Includes co-generation of a companion report. Follows Superagent's observed sequence: planning, scaffolding, content, styling, data viz, review, bundle.

## Acceptance Criteria
- [ ] 7-stage pipeline: planning -> scaffolding -> content -> styling -> data viz -> review -> bundle
- [ ] Output stored as Manifest with individual files as Artifacts
- [ ] Root Artifact tagged entity_type=GENERATED_WEBSITE
- [ ] Manifest includes at minimum: index.html, styles.css
- [ ] `GET /api/v1/manifests/{sha256}` returns the bundle tree
- [ ] AI message hydrated_content includes both `<gml-ViewWebsite>` and `<gml-ViewReport>`
- [ ] REPORT_PREVIEW_START/DELTA per stage, MANIFEST_CREATED, REPORT_PREVIEW_DONE events emitted
- [ ] Co-generation: also triggers report generation (companion artifact)

## Technical Notes
- Net-new file: `src/intelli/agents/graphs/nodes/website_generation.py`
- Uses existing Artifact/Manifest storage (already working)
- Each file = separate Artifact; Manifest groups them into bundle
- Co-generation pattern: both gml-ViewWebsite and gml-ViewReport in AI response (confirmed from chat export)
- See IMPLEMENTATION-PLAN.md Section 2.3 for full pipeline detail

### Sub-Issues

#### [BL-006a] Website Planning and Scaffolding (Stages 1-2)
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:high`, `track:deliverables`, `size:M`
- LLM determines page structure and tech stack
- Generates HTML/CSS/JS skeleton per page
- Emits REPORT_PREVIEW_START and REPORT_PREVIEW_DELTA events

#### [BL-006b] Content, Styling, and Data Viz (Stages 3-5)
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:high`, `track:deliverables`, `size:M`
- Fill sections from DataBrief, refine CSS/typography
- Embed charts and tables from research data
- REPORT_PREVIEW_DELTA per stage

#### [BL-006c] Review, Bundle, and Co-Generation (Stages 6-7)
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:high`, `track:deliverables`, `size:M`
- LLM critique and fix pass
- Assemble Manifest: each file as Artifact, root = index.html
- Trigger companion report generation via arq
- Emit MANIFEST_CREATED and REPORT_PREVIEW_DONE

## References
- BACKLOG.md: BL-006
- IMPLEMENTATION-PLAN.md: Section 2.3

---