# [BL-015] DeliverableStore (Zustand)
**Labels:** `type:frontend`, `phase:0-foundation`, `priority:medium`, `track:frontend`, `size:XS`
**Milestone:** M0: Foundation
**Blocked By:** None
**Blocks:** None

**Body:**
## Overview
Create the 6th Zustand store to manage deliverable selection state and active preview state. Tracks which deliverable type is selected, whether generation is in progress, current generation phase label, and async entity creation status.

## Acceptance Criteria
- [ ] Store interface includes: selectedType, activePreview (artifactSha256, manifestSha256, isGenerating, generationPhase, generationProgress, hasAsyncEntitiesInProgress)
- [ ] All action methods typed: setSelectedType, setGenerationPhase, setActiveArtifact, setAsyncEntitiesInProgress, clearPreview
- [ ] Store compiles with no TypeScript errors
- [ ] Exported correctly alongside existing 5 stores

## Technical Notes
- Net-new file: `ui/src/stores/deliverable-store.ts`
- Existing stores: auth-store.ts, conversation-store.ts, workbench-store.ts, run-store.ts, tour-store.ts
- `generationProgress` is 0-100 numeric
- `generationPhase` is human-readable string like "Writing outline..." or "Building components..."

## References
- BACKLOG.md: BL-015
- IMPLEMENTATION-PLAN.md: Section 3.1

---