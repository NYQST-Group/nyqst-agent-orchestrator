# [P0-001] Fix arq worker job registration (WorkerSettings.functions empty)

**Why this matters**
The arq worker currently boots with an empty `functions` list because `WorkerSettings.functions` is evaluated before jobs are registered. That means background ingestion jobs will never run when you start `arq intelli.core.jobs.WorkerSettings`.

**Repo evidence**
- `src/intelli/core/jobs.py` defines `WorkerSettings` before `@job(...)` functions, and sets `functions = list(_job_registry.values())` at class definition time (registry still empty).

**Goal**
- Worker starts and can execute registered jobs (e.g., `parse_document_job`) without manual patching.

**Implementation (recommended)**
1. In `src/intelli/core/jobs.py`, ensure `WorkerSettings.functions` is populated *after* all jobs are registered.
   - Option A (cleanest): move `class WorkerSettings` to the bottom of the module (after all `@job` decorated functions).
   - Option B: keep class where it is, but set `WorkerSettings.functions = list(_job_registry.values())` at the end of the file after job registration.
2. Confirm arq expects callables, not names/strings (keep a list of callables).
3. Add a minimal integration test (or smoke script) that imports `WorkerSettings` and asserts `parse_document_job` is included in `WorkerSettings.functions`.

**Acceptance criteria**
- Starting the worker (`arq intelli.core.jobs.WorkerSettings`) no longer logs “0 functions registered”.
- A queued `parse_document_job` executes end-to-end and persists expected outputs.

**Test plan**
- Unit: import `WorkerSettings` and assert non-empty.
- Integration: enqueue a document parse job, confirm completion + created artifacts.
