---
    key: STORY-STREAM-001
    title: Streaming protocol alignment (NDJSON/SSE), heartbeat, reconnect
    type: story
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:M, track:platform, type:story]
    ---

    ## Problem

    Production streaming needs heartbeat, reconnect/backoff, and consistent framing (NDJSON over fetch or SSE).

    ## Proposed solution

    Implement server heartbeat + client watchdog; choose framing (SSE or NDJSON) and ensure end-to-end fixtures and reconnection behavior.

    ## Dependencies

    - TASK-CON-002 — Implement run_event schema + fixtures + validators
- EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] Server sends heartbeat when idle (configurable interval)
- [ ] Client reconnects with exponential backoff up to max attempts
- [ ] Done event terminates stream cleanly and includes async-pending flags when relevant
- [ ] Fixtures include heartbeat and reconnect scenarios

    ## Test plan

    - [ ] Integration: stream emits heartbeat
- [ ] Frontend unit: reconnect state machine
- [ ] E2E: simulate drop and reconnect without losing ordering

    ## Notes / references

    - See COMPRESSED-BUILD-SPEC.md Domain A streaming behaviors
