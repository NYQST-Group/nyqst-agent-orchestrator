# [BL-007] PlanViewer Component
**Labels:** `type:frontend`, `phase:3-frontend`, `priority:high`, `track:frontend`, `size:M`
**Milestone:** M3: Frontend
**Blocked By:** BL-002
**Blocks:** None

**Body:**
## Overview
Create a plan visualization component showing numbered task cards with live status indicators, inspired by Superagent's activity panel. Tasks are grouped by phase and update in real-time via SSE events. Renders in a new "Plan" tab within the existing DetailsPanel.

## Acceptance Criteria
- [ ] Task cards appear immediately on receiving PLAN_CREATED event
- [ ] Each card shows: numbered badge, task name, phase grouping header
- [ ] Status updates live: pending (gray) -> processing (amber) -> completed (green) / failed (red)
- [ ] Failed tasks show error message in tooltip
- [ ] Duration shown on completed tasks
- [ ] Renders in new "Plan" tab in DetailsPanel.tsx
- [ ] Empty state when no plan exists for the current run

## Technical Notes
- Net-new file: `ui/src/components/plans/PlanViewer.tsx`
- Data source: PLAN_CREATED (initial list), PLAN_TASK_STARTED/COMPLETED/FAILED (live updates)
- Modify: `ui/src/components/workbench/DetailsPanel.tsx` to add Plan tab
- Event wiring via existing `use-sse.ts` hook
- Left border color indicates status; visual style per IMPLEMENTATION-PLAN.md Section 3.4

## References
- BACKLOG.md: BL-007
- IMPLEMENTATION-PLAN.md: Section 3.4

---