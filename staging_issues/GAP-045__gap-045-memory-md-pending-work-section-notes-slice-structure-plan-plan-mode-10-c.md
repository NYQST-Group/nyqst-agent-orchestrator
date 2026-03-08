# [GAP-045] MEMORY.md (Pending Work section) notes: "Slice structure plan (plan mode): 10 CLAUDE.md team briefs in dev repo — approved but not yet created." The 10 team briefs are the primary onboarding and context documents for AI agent subteams working in parallel on the 5 tracks. Without these briefs, each agent team must reconstruct context from the full document corpus, which violates the "NEVER read full source files" context management rule and will cause compounding context errors across parallel tracks.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-045
- **Severity**: LOW
- **Description**: MEMORY.md (Pending Work section) notes: "Slice structure plan (plan mode): 10 CLAUDE.md team briefs in dev repo — approved but not yet created." The 10 team briefs are the primary onboarding and context documents for AI agent subteams working in parallel on the 5 tracks. Without these briefs, each agent team must reconstruct context from the full document corpus, which violates the "NEVER read full source files" context management rule and will cause compounding context errors across parallel tracks.
- **Affected BL Items**: All BL items — affects parallel execution quality
- **Source Evidence**: MEMORY.md Pending Work; KNOWLEDGE-MAP Section 9 (Critical Knowledge Paths)
- **Resolution**: Create the 10 CLAUDE.md team briefs in the dev repo, each 1–2 pages covering: team scope, assigned BL items, key decisions (relevant DEC-xxx), dependencies on other teams, files they own, files they must not modify. This is a 1-day documentation task. Approved by user but not yet executed.
- **Owner Recommendation**: Engineering lead / plan owner
- **Wave**: P0 — must exist before any parallel agent execution

---

## Cross-Cutting Observations

### Propagation Debt Pattern

The most pervasive gap class is **propagation debt**: decisions are made correctly in the Decision Register but are not written back to the source documents where they will be read by implementers. The project has strong decision hygiene (52+ locked decisions) but poor propagation hygiene. The CONSISTENCY-AUDIT-PLANS document correctly identifies all required propagations but is itself an intermediate artifact — the propagations still need to be applied.

Estimated propagation debt resolution: 2–3 engineer-days of documentation work before Wave 0 implementation begins.

### Production Bug Risk

Two production-blocking bugs (GAP-022, GAP-023) were confirmed by direct codebase inspection. These are not theoretical risks — they are real code paths that will fail under the exact conditions (parallel fan-out writes, arq job execution) that the BL-001 and BL-016 implementations will trigger. Both bugs have straightforward fixes (≤ 4 hours each) but must be in place before any implementation that depends on them.

### Phase 0 Validation Checkpoint Is Critical

The six-task Phase 0 validation checklist (GAP-039) is the single highest-leverage risk-reduction action available. Running these validations before any Wave 1 code is written will expose hidden infrastructure failures (arq worker, WeasyPrint system deps, API key validity) in a low-cost, low-stakes context rather than mid-implementation.

---

## Prioritized Resolution Order

### P0 — Before Any Code Is Written (Estimated: 3–4 engineer-days)

1. **GAP-022** — Fix sequence number race condition (CRITICAL, 4 hours)
2. **GAP-023** — Fix arq worker registry initialization (CRITICAL, 4 hours)
3. **GAP-001** — Propagate Plotly decision to 4 documents (CRITICAL, 2 hours)
4. **GAP-002** — Propagate GML rendering split to affected docs (CRITICAL, 2 hours)
5. **GAP-003** — Mark OQ-001–007 as resolved in source documents (CRITICAL, 3 hours)
6. **GAP-009** — Correct 8 blocked-by fields in GIT-ISSUES (MEDIUM, 1 hour)
7. **GAP-010** — Move BL-015 and BL-008 to Wave 0 milestone (MEDIUM, 30 minutes)
8. **GAP-011** — Flip BL-022 dependency arrow in IMPLEMENTATION-PLAN (MEDIUM, 15 minutes)
9. **GAP-008** — Apply SC-01 through SC-07 stale claim corrections (MEDIUM, 2 hours)
10. **GAP-039** — Formalize Phase 0 validation checklist in IMPLEMENTATION-PLAN (HIGH, 2 hours)
11. **GAP-045** — Create 10 CLAUDE.md team briefs in dev repo (LOW, 8 hours)

### W0 — Phase 0 Foundation (Estimated: 1 engineer-week parallel with implementation)

12. **GAP-014** — Create formal Event Contract v1 document (CRITICAL, 4 hours)
13. **GAP-017** — Formalize NDM v1 JSON schema (HIGH, 4 hours)
14. **GAP-038** — Create minimal CI pipeline (CRITICAL, 1 day)
15. **GAP-028** — Document MIG-0005A/b/c content (MEDIUM, 2 hours)
16. **GAP-015** — Document tool fallback chain in BL-001 spec (HIGH, 2 hours)
17. **GAP-025** — Langfuse deployment specification (HIGH, 2 hours)
18. **GAP-026** — Search provider cost comparison and lock (HIGH, 2 hours)
19. **GAP-018** — Specify MCP tool discovery algorithm (HIGH, 2 hours)
20. **GAP-021** — Enumerate failure modes in BL-001 spec (MEDIUM, 2 hours)
21. **GAP-043** — Specify v1 tenant isolation approach (MEDIUM, 2 hours)
22. **GAP-041** — Create developer setup guide (MEDIUM, 4 hours)
23. **GAP-004** — Add deferred scope section to IMPLEMENTATION-PLAN (HIGH, 1 hour)
24. **GAP-005** — Add Index Service to platform primitives list (HIGH, 30 minutes)
25. **GAP-006** — Add document processing pipeline decision (HIGH, 1 hour)
26. **GAP-007** — Add infrastructure decision to DECISION-REGISTER (MEDIUM, 1 hour)
27. **GAP-012** — Update router count in PLATFORM-GROUND-TRUTH (LOW, 5 minutes)
28. **GAP-013** — Add `<answer>` wrapper spec to GML-RENDERING-ANALYSIS (LOW, 30 minutes)
29. **GAP-030** — Decide feature flag mechanism for v1 (MEDIUM, 1 hour)

### W1 — Phase 1 Build

30. **GAP-016** — Create BL-023 (async entity worker backlog item) (HIGH, 1 hour)
31. **GAP-024** — Decision: LiteLLM in v1 critical path? (HIGH, 2-hour design discussion)
32. **GAP-029** — Inspect and verify DocuIntelli billing code (MEDIUM, 4 hours)
33. **GAP-019** — Specify HITL policy evaluation order (MEDIUM, 2 hours)
34. **GAP-020** — Specify entity reference algorithm edge cases (MEDIUM, 2 hours)
35. **GAP-031** — Specify slides generation pipeline (LOW, 2 hours)
36. **GAP-032** — Specify clarification resume endpoint (LOW, 1 hour)
37. **GAP-040** — Define production monitoring and alerting (HIGH, 1 day)
38. **GAP-042** — Define staging environment (MEDIUM, 2 hours)
39. **GAP-036** — Clarify gml-viewgenerateddocument scope (MEDIUM, 1 hour)

### W2 — Phase 2 Build

40. **GAP-044** — Data retention and backup policy (LOW, 2 hours)
41. **GAP-033** — Validate GML spec against live reference (HIGH, 4 hours)
42. **GAP-027** — Assess Neo4j Aura free tier limits (MEDIUM, 1 hour)

### W3 / Post-v1

43. **GAP-034** — Superagent auth method assessment (MEDIUM — enterprise shell)
44. **GAP-035** — SSO design for enterprise tier (MEDIUM — enterprise shell)
45. **GAP-037** — Product analytics gap for enterprise (LOW — Layer 3)

---

*Revision Log:*

| Date | Author | Change |
|------|--------|--------|
| 2026-02-20 | Claude Sonnet 4.6 (Senior Engineering Lead role) | Initial comprehensive gap analysis — synthesizes all hypothesis tests, inventory data, extract documents, and consistency audits |