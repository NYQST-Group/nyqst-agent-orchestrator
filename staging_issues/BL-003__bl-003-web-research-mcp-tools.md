# [BL-003] Web Research MCP Tools
**Labels:** `type:integration`, `phase:1-orchestrator`, `priority:critical-path`, `track:orchestrator`, `size:M`
**Milestone:** M1: Orchestrator
**Blocked By:** None (standalone tools); BL-001 (integration wiring into orchestrator)
**Blocks:** BL-011

**Body:**
## Overview
Add web research tools (Brave Search and Jina Reader) to the agent's tool arsenal. These are registered as MCP tools alongside the existing search_documents, list_notebooks, get_document_info, and compare_manifests. Each invocation emits the corresponding WEB_SEARCH_* / WEB_SCRAPE_* RunEvents via the ledger.

> **Note:** Brave/Jina API wrappers can be built and tested independently in Wave 0. Integration into research_worker_node requires BL-001 (Wave 2).

## Acceptance Criteria
- [ ] `brave_web_search(query, count)` returns search results from Brave Search API
- [ ] `jina_web_scrape(url)` returns cleaned text content from Jina Reader API
- [ ] Both tools registered in MCP server alongside existing tools
- [ ] WEB_SEARCH_STARTED/COMPLETED events emitted on each search invocation
- [ ] WEB_SCRAPE_STARTED/COMPLETED events emitted on each scrape invocation
- [ ] Timeouts configured: 15s for Brave, 30s for Jina
- [ ] API keys read from config: BRAVE_SEARCH_API_KEY, JINA_API_KEY

## Technical Notes
- Net-new MCP registration file: `src/intelli/mcp/tools/research_tools.py` (distinct from `agents/tools/research_tools.py`)
- Register in `src/intelli/mcp/server.py`
- Brave endpoint: `https://api.search.brave.com/res/v1/web/search`
- Jina endpoint: `https://r.jina.ai/{url}`
- Uses httpx.AsyncClient for both
- See IMPLEMENTATION-PLAN.md Section 1.3 for implementation detail

## References
- BACKLOG.md: BL-003
- IMPLEMENTATION-PLAN.md: Section 1.3

---