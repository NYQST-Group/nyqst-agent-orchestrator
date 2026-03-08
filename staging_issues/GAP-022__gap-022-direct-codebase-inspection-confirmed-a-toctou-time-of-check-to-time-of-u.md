# [GAP-022] Direct codebase inspection confirmed a TOCTOU (time-of-check-to-time-of-use) race condition in `src/intelli/repositories/runs.py` `_get_next_sequence` method. The method SELECT MAX(sequence_num) then INSERT with MAX+1. Under concurrent parallel task execution (which BL-001 Send() fan-out will trigger), multiple tasks can SELECT the same MAX value and attempt to INSERT with the same sequence_num+1, violating the unique constraint `(run_id, sequence_num)`. This causes data corruption in the run ledger under load.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-022
- **Severity**: CRITICAL
- **Description**: Direct codebase inspection confirmed a TOCTOU (time-of-check-to-time-of-use) race condition in `src/intelli/repositories/runs.py` `_get_next_sequence` method. The method SELECT MAX(sequence_num) then INSERT with MAX+1. Under concurrent parallel task execution (which BL-001 Send() fan-out will trigger), multiple tasks can SELECT the same MAX value and attempt to INSERT with the same sequence_num+1, violating the unique constraint `(run_id, sequence_num)`. This causes data corruption in the run ledger under load.
- **Affected BL Items**: BL-001 (fan-out creates concurrent writes), BL-002 (RunEvent schema)
- **Source Evidence**: hypothesis-code-alignment.md H7.1 (bug confirmed in production code)
- **Resolution**: Fix `_get_next_sequence` before implementing BL-001 fan-out. Three options: (1) Replace SELECT MAX with `SEQUENCE` or `GENERATED ALWAYS AS IDENTITY` at DB level (cleanest); (2) Use `SELECT FOR UPDATE` with `SERIALIZABLE` isolation; (3) Move to DB-level trigger. Recommend option 1: add `sequence_num BIGINT GENERATED ALWAYS AS IDENTITY` to RunEvent in Migration 0005. Create INFRA-BUG-001 tracking issue.
- **Owner Recommendation**: Backend track lead — must fix before any BL-001 work begins
- **Wave**: P0 — production-blocking; blocks BL-001

---

### GAP-023 — P0 Bug: ARQ Worker Registry Initialization Order