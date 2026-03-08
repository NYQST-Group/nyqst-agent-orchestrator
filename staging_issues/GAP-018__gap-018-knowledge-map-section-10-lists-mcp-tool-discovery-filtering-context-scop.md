# [GAP-018] KNOWLEDGE-MAP Section 10 lists "MCP tool discovery filtering (context-scoped, needs algorithm for 'is tool X relevant to session Y?')" as a needed-soon open thread. ADR-008 specifies MCP as the tool protocol with session-scoped discovery. DEC-046 locks MCP search (hot-swap Brave/Tavily). However, the algorithm for how the orchestrator decides which MCP tools are available in a given session context is not specified. This matters because the Research Orchestrator (BL-001) must know which tools to include in a given PlanTask.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-018
- **Severity**: HIGH
- **Description**: KNOWLEDGE-MAP Section 10 lists "MCP tool discovery filtering (context-scoped, needs algorithm for 'is tool X relevant to session Y?')" as a needed-soon open thread. ADR-008 specifies MCP as the tool protocol with session-scoped discovery. DEC-046 locks MCP search (hot-swap Brave/Tavily). However, the algorithm for how the orchestrator decides which MCP tools are available in a given session context is not specified. This matters because the Research Orchestrator (BL-001) must know which tools to include in a given PlanTask.
- **Affected BL Items**: BL-001 (orchestrator tool selection), BL-003 (MCP tool definitions)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; ADR-008; orchestration-extract.md Section 2.1 (tool dispatch)
- **Resolution**: Specify the tool discovery algorithm in BL-001 technical notes: (1) On session creation, register available MCP tools based on tenant tier (sandbox: subset, professional: full); (2) On PlanTask creation, filter tool list by task category (financial_data → FactSet chain; web_search → Brave/Tavily; document → DocIR tools); (3) Pass filtered tool list to research_executor node.
- **Owner Recommendation**: Backend architecture lead
- **Wave**: W0

---

### GAP-019 — Policy Evaluation Order for HITL Not Specified