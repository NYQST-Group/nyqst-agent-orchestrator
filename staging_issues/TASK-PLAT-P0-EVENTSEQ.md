---
    key: TASK-PLAT-P0-EVENTSEQ
    title: P0: Fix RunEvent sequence_num race condition
    type: task
    milestone: M0 Baseline + P0 fixes
    labels: [phase:0-baseline, priority:critical, size:S, track:platform, type:task]
    ---

    ## Problem

    Parallel event writers can collide on sequence_num, causing IntegrityError and breaking fan-out.

    ## Proposed solution

    Make append_event use atomic insert with sequence subquery, with bounded retries.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] 10 concurrent append_event calls for same run succeed
- [ ] sequence_num are contiguous and unique (1..10)
- [ ] no IntegrityError under normal concurrency

    ## Test plan

    - [ ] Unit/integration test for concurrent append_event

    ## Notes / references

    - Mirror P0-2 fix
