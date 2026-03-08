# [GAP-026] DEC-046 specifies MCP search with hot-swap Brave/Tavily. KNOWLEDGE-MAP Section 10 lists "Search provider selection (Brave API vs Tavily, cost comparison needed)" as an external dependency TBD. DEC-032 (original) locked Brave Search API, superseded by DEC-046 which adds Tavily as an alternative but does not select between them. BL-003 (web research MCP tools) must implement one as the default with the other as the fallback — but which is primary is not specified.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-026
- **Severity**: HIGH
- **Description**: DEC-046 specifies MCP search with hot-swap Brave/Tavily. KNOWLEDGE-MAP Section 10 lists "Search provider selection (Brave API vs Tavily, cost comparison needed)" as an external dependency TBD. DEC-032 (original) locked Brave Search API, superseded by DEC-046 which adds Tavily as an alternative but does not select between them. BL-003 (web research MCP tools) must implement one as the default with the other as the fallback — but which is primary is not specified.
- **Affected BL Items**: BL-003 (MCP web research tools)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; DEC-046; hypothesis-consistency.md H4 (tool fallback)
- **Resolution**: Conduct Brave vs Tavily cost comparison (API pricing per 1000 queries, rate limits, result quality for financial/regulatory queries). Lock a decision specifying primary and fallback. This is an operational/procurement decision that must precede BL-003 implementation. Estimated effort: 2-hour research task.
- **Owner Recommendation**: Product / engineering lead
- **Wave**: W0 — before BL-003

---

### GAP-027 — Neo4j Aura Free Tier Limits Not Assessed