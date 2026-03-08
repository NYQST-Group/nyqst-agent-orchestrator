# [GAP-023] Direct codebase inspection confirmed that `WorkerSettings.functions` in `src/intelli/core/jobs.py` is evaluated as a class variable at class definition time (module import). At that point, `_job_registry` is still empty because the `@job()` decorators on functions defined below `WorkerSettings` have not yet run. The result: ARQ worker starts with an empty functions list and silently ignores all job submissions. This means any code relying on arq background workers (BL-016 async entity creation, BL-012 billing batch jobs) will appear to work but jobs will never execute.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-023
- **Severity**: CRITICAL
- **Description**: Direct codebase inspection confirmed that `WorkerSettings.functions` in `src/intelli/core/jobs.py` is evaluated as a class variable at class definition time (module import). At that point, `_job_registry` is still empty because the `@job()` decorators on functions defined below `WorkerSettings` have not yet run. The result: ARQ worker starts with an empty functions list and silently ignores all job submissions. This means any code relying on arq background workers (BL-016 async entity creation, BL-012 billing batch jobs) will appear to work but jobs will never execute.
- **Affected BL Items**: BL-016 (async entity creation), BL-012 (billing batch jobs)
- **Source Evidence**: hypothesis-code-alignment.md H7.2 (bug confirmed in production code)
- **Resolution**: Fix `WorkerSettings.functions` before implementing BL-016 or any arq-dependent work. Fix options: (1) Use `@property` or callable for late binding; (2) Move `WorkerSettings` to a separate module loaded after all job definitions; (3) Use `__init_subclass__` pattern. Recommend option 2 as simplest: create `src/intelli/core/worker_settings.py` that imports from `jobs.py` (ensuring decorator execution order). Also verifies GAP-016's prerequisite: arq must be confirmed operational before BL-016 begins. Create INFRA-BUG-002 tracking issue.
- **Owner Recommendation**: Backend track lead; prerequisite for arq operational verification (CONSISTENCY-AUDIT-PLANS SC-01)
- **Wave**: P0 — production-blocking; must fix before Wave 0 arq verification checkpoint

---

## Category 3: Implementation Gaps

### GAP-024 — LiteLLM Integration: Designed but Not Coded