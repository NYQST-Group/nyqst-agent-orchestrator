# [BL-011] Enhanced SourcesPanel
**Labels:** `type:frontend`, `phase:3-frontend`, `priority:medium`, `track:frontend`, `size:M`
**Milestone:** M3: Frontend
**Blocked By:** BL-003, BL-016
**Blocks:** None

**Body:**
## Overview
Enhance the existing SourcesPanel component to add a "Web Sources" tab alongside the existing RAG documents tab. Web sources are fetched from the entity API endpoint and display favicon, title, URL, snippet, and relevance badge. The existing SourcesPanel.tsx, SourcesContext.tsx, and use-thread-sources.ts hook are preserved and extended.

## Acceptance Criteria
- [ ] "Web Sources" tab appears when run has WEB_SOURCE entity artifacts
- [ ] Each source displays: favicon (via Google favicons API), title, URL, snippet
- [ ] Relevance badge shown per source
- [ ] Click opens source URL in new tab
- [ ] Count badge on tab shows source count
- [ ] Existing RAG sources tab completely unaffected
- [ ] Data fetched from `GET /api/v1/runs/{run_id}/entities?entity_type=web_source`

## Technical Notes
- Extends existing: `ui/src/components/chat/SourcesPanel.tsx`
- Understand existing SourcesContext.tsx and use-thread-sources.ts data shape before modifying
- Favicon URL pattern: `https://www.google.com/s2/favicons?domain={domain}`
- See IMPLEMENTATION-PLAN.md Section 3.7
- Sources panel needs entity API endpoint from BL-016 for web_source entities.

## References
- BACKLOG.md: BL-011
- IMPLEMENTATION-PLAN.md: Section 3.7

---