# PLUG-002 — Implement MCP knowledge tools (documents, notebooks, web research) and wire into graphs

- Type: **story**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `mcp`, `tools`
- Depends on: `PLUG-001`, `BL-003`

## Problem

`knowledge_tools.py` is stubbed. Without it, tools cannot be exposed uniformly or reused across apps/workflows.

## Proposed solution

Implement MCP knowledge tools:
- `knowledge.search_documents` (RAG search with filters)
- `knowledge.fetch_document` (artifact fetch, snippets)
- `knowledge.search_web` (Brave/Tavily)
- `knowledge.fetch_page` (Jina Reader)

Add LangChain tool wrappers that call MCP tools so graphs can use them transparently.

## Repo touchpoints

- `src/intelli/mcp/tools/knowledge_tools.py`
- `src/intelli/agents/tools/*`

## Acceptance criteria

- MCP knowledge tools respond correctly and return structured outputs.
- Graphs can call the MCP-wrapped tools and store outputs as artifacts.

## Test plan

- Integration: MCP server responds; tool wrapper works in a graph run.
