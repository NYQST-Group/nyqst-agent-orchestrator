# Sanitization Manifest

This manifest restores provenance for materially rewritten staged issues without retrofitting inline `> V4 OVERRIDE:` headers into the authoritative files under `staging_issues/`.

## Provenance Model
- Authoritative staged corpus: `staging_issues/`
- Manifest date: `2026-03-11`
- Legacy pack tree available in current repository: `false`
- Reason for manifest model: the final staged issue text is authoritative and readable, but it no longer retains the inline override banners originally specified in the historical sanitization track.

## Entries

### BL-004
- Staging files: `BL-004.md`, `BL-004a.md`, `BL-004b.md`, `BL-004__bl-004-nyqst-markup-ast-schema.md`
- Legacy source lineage: `packs/V2/issues/BL-004*`
- Applied decisions: `DEC-V4-048`, `GAP-001`
- Rationale: charting and rendering assumptions were aligned to the V4 stack while preserving the split staging output already imported from this corpus.

### BL-005
- Staging files: `BL-005.md`, `BL-005a.md`, `BL-005b.md`, `BL-005c.md`, `BL-005__bl-005-report-generation-node.md`
- Legacy source lineage: `packs/V2/issues/BL-005*`
- Applied decisions: `DEC-V4-048`, `GAP-001`
- Rationale: reporting-node expectations were normalized around the current rendering and charting direction rather than legacy Recharts assumptions.

### BL-009
- Staging files: `BL-009.md`, `BL-009__bl-009-reportrenderer-component.md`
- Legacy source lineage: `packs/V2/issues/BL-009*`
- Applied decisions: `DEC-V4-048`, `GAP-001`
- Rationale: renderer behavior was preserved, but visualization references were aligned to the V4 charting choice.

### BL-019
- Staging files: `BL-019.md`, `BL-019a.md`, `BL-019b.md`, `BL-019c.md`, `BL-019__bl-019-document-deliverable-pdf-docx-export.md`
- Legacy source lineage: `packs/V2/issues/BL-019*`
- Applied decisions: `DEC-V4-048`, `GAP-001`
- Rationale: deliverable export requirements were kept, while conflicting legacy charting assumptions were removed from the staged corpus.

### EPIC-P0
- Staging files: `EPIC-P0.md`
- Legacy source lineage: `packs/V2/issues/EPIC-P0.md`
- Applied decisions: `DEC-V4-008`
- Rationale: orchestration and scheduling language was aligned to `arq` plus cron-based execution rather than Temporal.

### STORY-PROD-004
- Staging files: `STORY-PROD-004.md`
- Legacy source lineage: `packs/V2M/issues/STORY-PROD-004.md`
- Applied decisions: `DEC-V4-008`
- Rationale: production scheduling expectations were trimmed to the supported worker model in V4.

### BL-007
- Staging files: `BL-007.md`, `BL-007a.md`, `BL-007__bl-007-planviewer-component.md`
- Legacy source lineage: `packs/V2/issues/BL-007*`
- Applied decisions: `DEC-V4-001`, `DEC-V4-003`
- Rationale: the staged plan-viewer issues preserve the feature intent while reflecting event-sourced plan state and tenant-aware streaming.

### P0-002
- Staging files: `P0-002.md`, `P0-002__p0-002-fix-runevent-sequence-num-race-unique-constraint-violations-under-concurr.md`
- Legacy source lineage: `packs/V2/issues/P0-002*`
- Applied decisions: `DEC-V4-001`, `DEC-V4-003`
- Rationale: concurrency and event-ordering work was aligned to `RunEvents` and tenant-aware streaming semantics.

### OBS-002
- Staging files: `OBS-002.md`
- Legacy source lineage: `packs/V2/issues/OBS-002.md`
- Applied decisions: `DEC-V4-001`, `DEC-V4-003`
- Rationale: observability expectations were aligned to the event-sourced run model and streaming constraints.

### STUDIO-001
- Staging files: `STUDIO-001.md`, `STORY-STUDIO-001.md`
- Legacy source lineage: `packs/V2/issues/STUDIO-001.md`
- Applied decisions: `DEC-V4-010`
- Rationale: studio scope was reduced to the supported V4 surface and non-essential integrations were deferred.

### STUDIO-002
- Staging files: `STUDIO-002.md`, `STORY-STUDIO-002.md`
- Legacy source lineage: `packs/V2/issues/STUDIO-002.md`
- Applied decisions: `DEC-V4-010`
- Rationale: the staged pair preserves the narrowed studio scope rather than the broader legacy integration model.

### STUDIO-003
- Staging files: `STUDIO-003.md`, `TASK-STUDIO-003.md`
- Legacy source lineage: `packs/V2/issues/STUDIO-003.md`
- Applied decisions: `DEC-V4-010`
- Rationale: the task split keeps the studio work actionable while reflecting the scope cuts recorded in V4.

### STUDIO-004
- Staging files: `STUDIO-004.md`, `STUDIO-004a.md`, `STUDIO-004b.md`, `STUDIO-004c.md`, `STORY-STUDIO-004.md`
- Legacy source lineage: `packs/V2/issues/STUDIO-004*`
- Applied decisions: `DEC-V4-010`
- Rationale: the staged cluster preserves the decomposed scope but excludes the cut integrations and workflow-editor assumptions from legacy planning.

### STUDIO-005
- Staging files: `STUDIO-005.md`
- Legacy source lineage: `packs/V2/issues/STUDIO-005.md`
- Applied decisions: `DEC-V4-010`
- Rationale: the remaining studio scope is retained without the removed integrations and broad visual-editor expectations.

## Notes
- `V4_OVERRIDE_TARGETS.md` remains the discovery index for the original override set.
- The current repository does not expose the original `packs/` tree used during staging, so this manifest records source lineage by historical path rather than live file references.
- Inline `V4 OVERRIDE` headers were intentionally not backfilled into the staged markdown because the staged files remain the authoritative import corpus.
