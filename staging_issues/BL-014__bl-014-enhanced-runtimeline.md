# [BL-014] Enhanced RunTimeline
**Labels:** `type:frontend`, `phase:3-frontend`, `priority:medium`, `track:frontend`, `size:M`
**Milestone:** M3: Frontend
**Blocked By:** BL-002
**Blocks:** None

**Body:**
## Overview
Enhance the existing RunTimeline/TimelinePanel to render all 19 new BL-002 event types with proper icons, labels, phase grouping, and subagent task cards. The timeline should remain flat for runs without a plan and group by phases when PLAN_CREATED is present.

## Acceptance Criteria
- [ ] All 19 new event types have distinct icons and human-readable labels (no raw enum fallback)
- [ ] Events grouped under collapsible phase headers when PLAN_CREATED is present
- [ ] Subagent task rows show compact card with task name, duration, tool call count
- [ ] CONTENT_DELTA events collapsed by default (expandable)
- [ ] Child run events surfaced inline under parent subagent card
- [ ] Timeline remains flat for runs without a plan (backward compatible)

## Technical Notes
- Check which file is active: `ui/src/components/workbench/TimelinePanel.tsx` vs `components/runs/RunTimeline.tsx`
- Extends existing component -- do not create a new timeline
- Phase grouping uses the phases array from PLAN_CREATED event payload

## References
- BACKLOG.md: BL-014
- IMPLEMENTATION-PLAN.md: Section 3.5

---