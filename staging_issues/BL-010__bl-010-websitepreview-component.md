# [BL-010] WebsitePreview Component
**Labels:** `type:frontend`, `phase:3-frontend`, `priority:medium`, `track:frontend`, `size:M`
**Milestone:** M3: Frontend
**Blocked By:** BL-006
**Blocks:** None

**Body:**
## Overview
Create a website preview component that fetches a generated website Manifest, loads the index.html as a blob URL, and renders it in a sandboxed iframe. Triggered by `<gml-ViewWebsite>` tags in AI message hydrated_content.

## Acceptance Criteria
- [ ] Fetches Manifest via `GET /api/v1/manifests/{sha256}`
- [ ] Locates index.html entry in Manifest tree
- [ ] Loads artifact content, creates blob URL, renders in sandboxed iframe
- [ ] iframe sandbox: `allow-scripts allow-same-origin`
- [ ] Blob URL properly revoked on component unmount (no memory leak)
- [ ] Loading state shown while fetching manifest and artifact

## Technical Notes
- Net-new file: `ui/src/components/deliverables/WebsitePreview.tsx`
- Uses existing Manifest and Artifact APIs (already working)
- Triggered by GmlComponentParser when it encounters `<gml-ViewWebsite>` tag
- See IMPLEMENTATION-PLAN.md Section 3.8

## References
- BACKLOG.md: BL-010
- IMPLEMENTATION-PLAN.md: Section 3.8

---