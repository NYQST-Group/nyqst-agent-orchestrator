# [BL-005] Report Generation Node
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:critical-path`, `track:deliverables`, `size:L`
**Milestone:** M2: Deliverables
**Blocked By:** BL-001, BL-004, MIG-0005A
**Blocks:** BL-016, BL-019, BL-009

**Body:**
## Overview
Create the report generation pipeline as a LangGraph node. Transforms research results via 4 passes (outline, section generation, review, assembly) into a MarkupDocument AST stored as an Artifact. Also handles co-generation (website requests produce a companion report). The report generation node is the primary deliverable pipeline.

## Acceptance Criteria
- [ ] 4-pass pipeline: outline -> parallel section generation -> review pass -> assembly + storage
- [ ] Output is a valid MarkupDocument JSON passing MarkupHealer.validate()
- [ ] Stored as Artifact with entity_type=GENERATED_REPORT
- [ ] AI message hydrated_content contains `<gml-ViewReport props='{"identifier": "{sha256}"}'>`
- [ ] message.first_report_identifier set to artifact sha256
- [ ] Citation IDs in document reference entities from data brief
- [ ] REPORT_PREVIEW_START/DELTA/DONE events emitted at appropriate stages
- [ ] Co-generation: triggered as companion when deliverable_type="website"

## Technical Notes
- Net-new file: `src/intelli/agents/graphs/nodes/report_generation.py`
- Parallel section gen uses Send() per section from outline
- MarkupHealer runs as safety net before storage
- Co-generation triggered via arq job queue when deliverable_type="website"
- Answer format: `<answer>...<gml-ViewReport props='{"identifier":"..."}'>...</answer>`
- See IMPLEMENTATION-PLAN.md Section 2.1 for full pipeline detail

### Sub-Issues

#### [BL-005a] Report Outline Pass
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:critical-path`, `track:deliverables`, `size:S`
- LLM call: DataBrief + query -> section outline
- Emit REPORT_PREVIEW_START event
- Output: list of section headings with assigned TaskResult data

#### [BL-005b] Parallel Section Generation
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:critical-path`, `track:deliverables`, `size:M`
- Send() per section from outline
- Each section LLM call produces MarkupNode subtree
- Citation IDs embedded from data_brief entities
- REPORT_PREVIEW_DELTA emitted per section

#### [BL-005c] Review Pass and Assembly
**Labels:** `type:feature`, `phase:2-deliverables`, `priority:high`, `track:deliverables`, `size:M`
- LLM review of full draft, targeted section rewrites
- Assembly: MarkupDocument construction, MarkupHealer validation
- Store as Artifact, set message.first_report_identifier
- Emit REPORT_PREVIEW_DONE + ARTIFACT_CREATED

## References
- BACKLOG.md: BL-005
- IMPLEMENTATION-PLAN.md: Section 2.1

---