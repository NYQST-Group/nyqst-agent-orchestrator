# [GAP-012] PLATFORM-GROUND-TRUTH.md states "11 routers" for the API surface. Direct codebase inspection (hypothesis-code-alignment.md H5) confirmed 12 routers — the tags router was added in migration 0004 and is not included in the documented count.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-012
- **Severity**: LOW
- **Description**: PLATFORM-GROUND-TRUTH.md states "11 routers" for the API surface. Direct codebase inspection (hypothesis-code-alignment.md H5) confirmed 12 routers — the tags router was added in migration 0004 and is not included in the documented count.
- **Affected BL Items**: None directly (documentation accuracy only)
- **Source Evidence**: hypothesis-code-alignment.md H5.5
- **Resolution**: Update PLATFORM-GROUND-TRUTH.md Section 5 (API Routes) from "11 routers" to "12 routers, including tags router added in migration 0004."
- **Owner Recommendation**: Documentation lead; 5-minute fix
- **Wave**: W0

---

### GAP-013 — `<answer>` Wrapper Stripping Not Addressed in GML Renderer Spec