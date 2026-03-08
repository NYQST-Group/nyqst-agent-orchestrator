# [BL-020] Generation Progress Overlay
**Labels:** `type:frontend`, `phase:3-frontend`, `priority:high`, `track:frontend`, `size:M`
**Milestone:** M3: Frontend
**Blocked By:** BL-002
**Blocks:** None

**Body:**
## Overview
Create a full-screen overlay that shows generation progress with dual-status display (primary action + substep), continuous progress indicator, and phase labels. Users tolerate 2+ minute waits when they see visible progress. Also handles the "Creating notes..." secondary state for async entity creation.

## Acceptance Criteria
- [ ] Overlay appears on REPORT_PREVIEW_START event, hides on REPORT_PREVIEW_DONE
- [ ] Shows deliverable type ("Generating your report...", "Building your website...")
- [ ] Phase label updates in real-time from REPORT_PREVIEW_DELTA payload
- [ ] Animated spinner and indeterminate progress bar displayed
- [ ] Secondary "Creating notes..." indicator shown while hasAsyncEntitiesInProgress is true
- [ ] Updates DeliverableStore: isGenerating, generationPhase, generationProgress
- [ ] Sets activePreview.artifactSha256 on REPORT_PREVIEW_DONE

## Technical Notes
- Net-new file: `ui/src/components/generation/GenerationOverlay.tsx`
- Wired to existing SSE via `use-sse.ts` hook -- do NOT add a new streaming mechanism
- Integrates with DeliverableStore (BL-015) for state management
- See IMPLEMENTATION-PLAN.md Section 3.3 for visual mockup

## References
- BACKLOG.md: BL-020
- IMPLEMENTATION-PLAN.md: Section 3.3

---