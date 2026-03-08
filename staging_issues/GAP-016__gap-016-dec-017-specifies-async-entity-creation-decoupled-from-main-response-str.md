# [GAP-016] DEC-017 specifies "Async entity creation: Decoupled from main response stream via arq background worker." PLATFORM-GROUND-TRUTH confirms `has_async_entities_in_progress` flag exists. BL-016 covers the entity/citation substrate schema. However, there is no dedicated backlog item for "Implement async entity creation worker" — the arq background job that processes entities after the main stream completes. The work is mentioned in DEC-017 and BL-016 body text but is not a standalone, estimable, assignable item.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-016
- **Severity**: HIGH
- **Description**: DEC-017 specifies "Async entity creation: Decoupled from main response stream via arq background worker." PLATFORM-GROUND-TRUTH confirms `has_async_entities_in_progress` flag exists. BL-016 covers the entity/citation substrate schema. However, there is no dedicated backlog item for "Implement async entity creation worker" — the arq background job that processes entities after the main stream completes. The work is mentioned in DEC-017 and BL-016 body text but is not a standalone, estimable, assignable item.
- **Affected BL Items**: BL-016 (entity substrate), adjacent to billing and observability
- **Source Evidence**: hypothesis-consistency.md H4 gap 5; CONSISTENCY-AUDIT-PLANS SC-05 (arq claim)
- **Resolution**: Create backlog item BL-023: "Async Entity Creation Worker — implement arq background job that processes entities after stream completion, triggered by `has_async_entities_pending: true` in the `done` event. Includes: job definition in jobs.py, entity resolution logic, `references_found` emission on completion." Size: ~1 SP.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1 — needed before BL-016 is considered complete

---

### GAP-017 — NDM v1 JSON Schema Not Formalized