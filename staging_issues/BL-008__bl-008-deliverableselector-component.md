# [BL-008] DeliverableSelector Component
**Labels:** `type:frontend`, `phase:0-foundation`, `priority:medium`, `track:frontend`, `size:S`
**Milestone:** M0: Foundation
**Blocked By:** BL-015 (weak — DeliverableSelector writes to useDeliverableStore)
**Blocks:** None

**Body:**
## Overview
Create a segmented control component positioned above the chat composer that lets users select the deliverable type (Report, Website, Slides, Document) before submitting a research query. Selection is stored in the DeliverableStore and included as `deliverable_type` on the user message payload.

## Acceptance Criteria
- [ ] Segmented control renders with 4 options: Report | Website | Slides | Document
- [ ] Each segment has an appropriate Lucide icon (FileText, Globe, Presentation, FileDown)
- [ ] Selection updates `useDeliverableStore().selectedType`
- [ ] Chat submit handler includes `deliverable_type` in the message request payload
- [ ] Selector auto-clears after submission (follow-up messages send `null`)
- [ ] Uses existing shadcn/ui ToggleGroup component

## Technical Notes
- Net-new file: `ui/src/components/chat/DeliverableSelector.tsx`
- Modify existing chat submit handler in ChatPanel.tsx to include deliverable_type
- Per chat export analysis: `deliverable_type` is on the user Message, not the Conversation
- Follow-up messages without explicit selection default to null

## References
- BACKLOG.md: BL-008
- IMPLEMENTATION-PLAN.md: Section 3.2

---