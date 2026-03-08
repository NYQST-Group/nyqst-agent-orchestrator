# [NX-007] Structured diffing for deliverables (report/markdown/doc) with provenance-aware highlights

**Goal**
When a deliverable is regenerated, users can see what changed and why:
- semantic diff at section level (not just line diff)
- each changed section shows the run/task/tool event that caused it

**Implementation**
- Store deliverable sections as structured JSON (or manifest tree nodes).
- Diff algorithm:
  - align sections by stable IDs
  - diff content with fallback to text diff
- UI:
  - “Compare versions” view
  - highlight changes and show provenance panel

**Acceptance criteria**
- Two versions of a report can be compared and differences are readable.
- Each diff chunk can link back to run events and citations.

