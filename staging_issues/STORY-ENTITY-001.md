---
    key: STORY-ENTITY-001
    title: Entity & citation system (entities, citations, buffers, matching)
    type: story
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:high, size:L, track:intelligence, type:story]
    ---

    ## Problem

    Agent outputs and extractions must resolve to entities and citations; without this, provenance is fragmented and hard to query.

    ## Proposed solution

    Implement entity objects (canonical), citations with source spans/URLs, a citation buffer pattern for async creation, and entity matching/merge flows.

    ## Dependencies

    - EPIC-INTEL — Evidence + insights + audit-first provenance
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- STORY-DOCS-004 — Pipeline: extraction to structured JSON + evidence spans

    ## Acceptance criteria

    - [ ] Entities can be created/updated/merged with audit
- [ ] Citations reference bundle version spans or web snapshots and link to entities/evidence
- [ ] Citation buffer supports async linking during runs
- [ ] UI can show citations for a run or insight and navigate to source

    ## Test plan

    - [ ] Integration: create citations during extraction and link to entity
- [ ] Unit: entity matching heuristics on fixtures

    ## Notes / references

    - Map to COMPRESSED-BUILD-SPEC.md Domain D and I.1 payload patterns
