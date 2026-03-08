# [GAP-015] Superagent's orchestration shows a clear tool failure cascade: FactSet → SEC Filings → AlphaVantage → FinancialModelingPrep. This "FALLBACK_CHAINS" pattern is documented in orchestration-extract.md Section 4.2 with explicit code. BL-001 (Research Orchestrator Graph) is the backlog item that must implement this pattern. However, BL-001's spec (MAPPING-01) does not explicitly design the fallback chain mechanism. The term "fallback" appears in the backlog context but the algorithm (try primary → emit fallback_used event → try secondary → emit all_tools_failed if all fail) is not in the spec.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-015
- **Severity**: HIGH
- **Description**: Superagent's orchestration shows a clear tool failure cascade: FactSet → SEC Filings → AlphaVantage → FinancialModelingPrep. This "FALLBACK_CHAINS" pattern is documented in orchestration-extract.md Section 4.2 with explicit code. BL-001 (Research Orchestrator Graph) is the backlog item that must implement this pattern. However, BL-001's spec (MAPPING-01) does not explicitly design the fallback chain mechanism. The term "fallback" appears in the backlog context but the algorithm (try primary → emit fallback_used event → try secondary → emit all_tools_failed if all fail) is not in the spec.
- **Affected BL Items**: BL-001, BL-003 (web research MCP tools that have fallback providers)
- **Source Evidence**: hypothesis-consistency.md H4 gap 4; orchestration-extract.md Section 4.1, 4.2
- **Resolution**: Amend BL-001 technical notes (MAPPING-01) to include the fallback chain algorithm: (1) Try primary provider, emit `tool_call_started`; (2) On failure: emit `node_tool_event(event="fallback_used")`; (3) Try secondary provider; (4) If all fail: emit `node_tool_event(event="all_tools_failed")` and mark task as partial; (5) Fan-in detects partial tasks and routes to meta-reasoning.
- **Owner Recommendation**: Backend track lead (BL-001 implementer)
- **Wave**: W0 — before BL-001 implementation begins

---

### GAP-016 — Async Entity Creation Worker Has No Dedicated Backlog Item