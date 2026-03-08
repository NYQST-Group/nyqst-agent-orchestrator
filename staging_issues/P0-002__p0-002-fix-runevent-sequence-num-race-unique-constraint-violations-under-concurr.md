# [P0-002] Fix RunEvent sequence_num race (unique constraint violations under concurrency)

**Why this matters**
`sequence_num` is computed as `MAX(sequence_num)+1` per run. Under concurrent inserts, this can collide and violate the unique constraint on `(run_id, sequence_num)`.

**Repo evidence**
- `src/intelli/repositories/runs.py` uses `_get_next_sequence()` which selects max + 1 without locking.

**Goal**
- Multiple concurrent event writes for the same run never fail (or retry safely).

**Implementation options**
- Preferred: acquire a per-run transactional advisory lock before selecting max+1, then insert.
  - Example: `SELECT pg_advisory_xact_lock(hashtext(:run_id::text));`
- Alternative: optimistic insert + retry on unique violation (loop with max+1 recompute).

**Acceptance criteria**
- Stress test: 100 concurrent inserts for same `run_id` produces 100 unique, strictly increasing sequence numbers with no errors.
- No measurable regression in single-writer throughput.

**Test plan**
- Add a concurrency test using `asyncio.gather()` with 50–200 emitters against a local Postgres.
