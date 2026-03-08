---
    key: EPIC-INTEL
    title: Evidence + insights + audit-first provenance
    type: epic
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:critical, size:XL, track:intelligence, type:epic]
    ---

    ## Problem

    The system must produce auditable intelligence: evidence supports insights; insights go stale on doc changes.

    ## Proposed solution

    Implement evidence and insight lifecycle, review queues, stale propagation, and provenance rules.

    ## Dependencies

    - EPIC-DOCUMENTS — Document management (bundles, versions, ingest, diff)
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Evidence always links to bundle version or web snapshot
- [ ] Insights require evidence links
- [ ] Stale insights flagged when upstream changes
- [ ] Review queue exists for low confidence/conflicts

    ## Test plan

    - [ ] Unit: stale propagation graph logic
- [ ] Integration: evidence/insight CRUD + linkage
- [ ] E2E: create insight then upload new doc version and see stale badge

    ## Notes / references

    - See docs/02_USER_FLOWS_MASTER.md Flow 2
