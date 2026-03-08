---
    key: TASK-CON-002
    title: Implement run_event schema + fixtures + validators
    type: task
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:S, track:platform, type:task]
    ---

    ## Problem

    Streaming UI depends on stable event envelopes and payload types.

    ## Proposed solution

    Finalize run_event.schema.json, add fixture streams (NDJSON/SSE), implement validators (backend and frontend dev assertions).

    ## Dependencies

    - STORY-CON-001 — Contract governance: versioning rules + fixtures discipline

    ## Acceptance criteria

    - [ ] run_event.schema.json exists and is used in tests
- [ ] At least 3 fixture streams exist: ingest run, app run, validation run
- [ ] Frontend can render fixture stream without runtime errors

    ## Test plan

    - [ ] Contract tests validate fixture streams

    ## Notes / references

    _None_
