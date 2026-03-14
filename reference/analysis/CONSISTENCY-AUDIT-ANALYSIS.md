---
document_id: CONSISTENCY-AUDIT-ANALYSIS
version: 1
date: 2026-02-19
scope: docs/analysis/
auditor: claude-sonnet-4-6
method: Cross-reference of 8 analysis documents against PLATFORM-GROUND-TRUTH.md and DECISION-REGISTER.md
---

# Consistency Audit — Analysis Document Set

## Audit Scope

Eight documents audited:

1. `CODEX-ANALYSIS-SUMMARY.md` — Codex platform assessment
2. `DIFY-ANALYSIS-SUMMARY.md` — Dify comparison
3. `OUR-ANALYSIS-SUMMARY.md` — 6-doc consolidated summary
4. `ANALYSIS-COMPARISON-CHECKPOINT.md` — Cross-analysis comparison (Opus, arbiter)
5. `LANGSMITH-COST-EVAL-RESEARCH.md` — Observability/cost research
6. `GML-RENDERING-ANALYSIS.md` — GML tag rendering strategy
7. `GRAPH-EDITOR-RESEARCH.md` — Graph editor options
8. `PLATFORM-GROUND-TRUTH.md` — Authoritative baseline (highest trust)

Decision Register cross-checked: `docs/plans/DECISION-REGISTER.md`

---

## Section 1: Ground Truth Violations

### Confirmed violations (already captured by COMPARISON-CHECKPOINT)

The COMPARISON-CHECKPOINT already identified and arbitrated Contradictions 1–7. The following confirms those were correctly captured and adds any missed items.

| Violation | Source | Ground Truth Fact | Severity |
|-----------|--------|-------------------|----------|
| "NYQST has NO server-side conversation model. Messages live in React state only." (Section 1.1) | DIFY-ANALYSIS-SUMMARY | Migration 0004 (2026-02-01) added conversations, messages, message_feedback, sessions, tags. Full CRUD API exists. | CRITICAL — already in CHECKPOINT |
| "Zero conversations are persisted; everything is client-side React state." (Section 6.1) | DIFY-ANALYSIS-SUMMARY | Same violation, restated in conclusions section | CRITICAL — already in CHECKPOINT |
| "NYQST has 11 tables" (Section 1.6) | DIFY-ANALYSIS-SUMMARY | 16 tables across 4 migrations | HIGH — already in CHECKPOINT |
| "Conversations + Messages" listed as "Critical missing tables (blocks MVP)" | DIFY-ANALYSIS-SUMMARY | These tables exist (migration 0004) | CRITICAL — already in CHECKPOINT |
| "Message feedback" listed as missing | DIFY-ANALYSIS-SUMMARY | message_feedback table exists (migration 0004); message-feedback.tsx in UI | HIGH — already in CHECKPOINT |
| "ResearchAssistantGraph is a 2-node pipeline: retrieve → generate. No tool calling, no branching, no loops." | DIFY-ANALYSIS-SUMMARY | 3-node StateGraph with ToolNode, conditional edges, 4 real tools | HIGH — already in CHECKPOINT |
| "NYQST emits ~10 event types" | DIFY-ANALYSIS-SUMMARY | RunEventType enum has 25 entries. The 10-event claim conflates the AI SDK chat stream with the platform run event taxonomy. | MEDIUM — partially captured in CHECKPOINT (conflation noted) |
| "NYQST vision: external agents orchestrate via MCP, NYQST does data" as a question (Section 6.3) | DIFY-ANALYSIS-SUMMARY | This is resolved by context: the platform IS building internal agent orchestration (DEC-012, DEC-013). The Dify analysis frames this as "clarify the strategy" but the strategy is locked. | LOW — not a factual error but stale framing |
| Framing NYQST as "early-stage prototype" in Executive Summary and Conclusion | DIFY-ANALYSIS-SUMMARY | 16 tables, 11 routers, working LangGraph agent, full auth, SSE, MCP tools, React frontend | MEDIUM — already in CHECKPOINT |

### New violations NOT captured by COMPARISON-CHECKPOINT

| Violation | Source | Ground Truth Fact | Severity |
|-----------|--------|-------------------|----------|
| GML-RENDERING-ANALYSIS Section 4 (JSON AST approach) describes a "JSON Render Approach" as a viable alternative but then recommends against it — however it still contains a full typed AST schema definition that assumes `GmlNode` types. DEC-015 has ALREADY LOCKED "JSON AST (NYQST Markup AST)" as the format. | GML-RENDERING-ANALYSIS | DEC-015: "Markup format: JSON AST (NYQST Markup AST), not raw HTML tags" | MEDIUM — The doc's RECOMMENDATION contradicts DEC-015. The doc recommends "rehype-to-JSX, skip the JSON AST layer." DEC-015 says JSON AST is the locked format. This is an unresolved conflict. |
| GML-RENDERING-ANALYSIS Section 5 describes GML as arriving in `node_report_preview_done` stream events. OUR-ANALYSIS-SUMMARY and TECHNICAL-DEEP-DIVE describe the LLM output as wrapped in `<answer>...</answer>` XML. DEC-022 locks `<answer>` wrapper format with `<gml-*>` tags inside. The GML rendering doc does not mention the `<answer>` wrapper at all. | GML-RENDERING-ANALYSIS | DEC-022: "LLM output wrapped in `<answer>...</answer>` XML; deliverables referenced via `<gml-*>` web component tags inside the wrapper" | LOW — The rendering pipeline assumes GML arrives pre-extracted from the answer wrapper. The parser must strip `<answer>` before passing to the GML renderer. The GML doc does not make this explicit. |
| OUR-ANALYSIS-SUMMARY item 4 in "Most Confident Findings" states: "4-node LangGraph (agent → tools → capture_sources)" but then parenthetically notes this is a 4-node graph when actually the Ground Truth describes it as a 3-node graph (agent, tools, capture_sources). The preceding description is a 3-step chain, not 4 nodes. | OUR-ANALYSIS-SUMMARY | Ground Truth: "3-node StateGraph" with agent, tools, capture_sources | LOW — Typo/miscounting in a confidence claim; the narrative description in Doc 4 of the same document is correct ("3-node graph"). |
| CODEX-ANALYSIS-SUMMARY Section 3.2 infrastructure matrix lists "Auth" as "Unresolved" with options "Supabase/Auth0/Ory/custom? SSO?" | CODEX-ANALYSIS-SUMMARY | DEC-038: "Auth: Use existing intelli auth (JWT + API keys) — NOT replicating Ory Kratos" — this is LOCKED | MEDIUM — Stale unresolved item already resolved by DEC-038. Not a ground truth violation but a stale open question that could mislead a plan restructure agent. |
| CODEX-ANALYSIS-SUMMARY Section 3.2 lists "Web search" as "Unresolved" | CODEX-ANALYSIS-SUMMARY | DEC-032: "Web search: Brave Search API" — LOCKED | MEDIUM — Same pattern: stale open question already resolved |
| CODEX-ANALYSIS-SUMMARY Section 3.2 lists "Model provider" as "Unresolved" | CODEX-ANALYSIS-SUMMARY | OQ-001 in DECISION-REGISTER is still open, so technically correct — but Codex frames it as broader than OQ-001, suggesting "multi-provider router" which is out of scope. | LOW — Partially stale framing; the real open question is narrower (OQ-001: Claude vs. OpenAI for orchestrator only) |
| CODEX-ANALYSIS-SUMMARY Section 2.3 describes "NYQST Markup v1" as "either JSON AST (recommended) or HTML-like tag set" | CODEX-ANALYSIS-SUMMARY | DEC-015: JSON AST is LOCKED. The "HTML-like tag set" option is dead. | MEDIUM — Already captured in COMPARISON-CHECKPOINT ("The 'HTML-like tag set' option is dead") but not explicitly listed as a violation table entry |
| LANGSMITH-COST-EVAL-RESEARCH Section 8.3 ("Automated Quality Eval After Each Run") uses `ls_client = Client()` from `langsmith` but also `from langfuse import Langfuse` elsewhere. Section 8.3 specifically writes evaluation feedback to LangSmith (`ls_client.create_feedback()`). The doc's recommendation is Langfuse self-hosted. There is a hybrid pattern mentioned but the example code in 8.3 mixes both tools without flagging this as a "hybrid setup." | LANGSMITH-COST-EVAL-RESEARCH | DEC-037: "Analytics/observability: Use existing Langfuse (not PostHog)". Langfuse is the locked observability choice. | LOW — Section 8.3 uses LangSmith SDK for feedback attachment. In a Langfuse-only setup, the `ls_client.create_feedback()` calls would need to use Langfuse's API instead. The code example is illustrative but partially wrong for our locked configuration. |

---

## Section 2: Inter-Summary Contradictions

| ID | Doc A | Doc B | Inconsistency | Resolution |
|----|-------|-------|---------------|-----------|
| C-01 | DIFY-ANALYSIS-SUMMARY: "NYQST has NO server-side conversation model" (Sections 1.1, 6.1, Phase 1 priority) | CODEX-ANALYSIS-SUMMARY: "Conversations table + message persistence exist" (Section 1.1) | Directly contradictory on a binary fact | CODEX is correct. Ground Truth confirms migration 0004. DIFY-ANALYSIS is wrong. |
| C-02 | DIFY-ANALYSIS-SUMMARY: "2-node pipeline: retrieve → generate. No tool calling." (Section 1.3) | CODEX-ANALYSIS-SUMMARY: 3-node graph with tool-use loop, named tools listed (Section 2.5) | Directly contradictory on agent graph architecture | CODEX and Ground Truth agree: 3-node graph, ToolNode with 4 real tools. DIFY is wrong. |
| C-03 | DIFY-ANALYSIS-SUMMARY: "NYQST has 11 tables" (Section 1.6) | CODEX-ANALYSIS-SUMMARY: "Migration 0004 added conversations/messages/sessions/tags" implying 16 tables (Section 4 claim 10) | Directly contradictory on table count | Ground Truth: ~16 tables. DIFY missed migration 0004. |
| C-04 | DIFY-ANALYSIS-SUMMARY: Phase 1 priority is "Conversation model (conversations + messages + feedback tables), 2–3 weeks" (Section 7) | OUR-ANALYSIS-SUMMARY: Doc 4 explicitly states 16 tables including conversations/messages already exist | The DIFY critical path proposes building something that already exists | Ground Truth resolves: this work is DONE. Remove from plan. |
| C-05 | DIFY-ANALYSIS-SUMMARY: "NYQST emits ~10 event types" (Section 1.7) | OUR-ANALYSIS-SUMMARY: "RunEventType enum has 25 event types (listed in full)" (Doc 4) | Contradictory on event taxonomy count | Both describe different things: DIFY refers to AI SDK chat stream events (~10–14 types in the Vercel AI SDK Data Stream Protocol). OUR-ANALYSIS refers to the platform RunEventType enum (25 types). Both numbers can be correct simultaneously for different systems. The DIFY framing ("NYQST emits ~10 event types") is misleading because it implies the platform event system is limited to 10, which is false. COMPARISON-CHECKPOINT Section 2, Contradiction 5 correctly identifies this as conflation. |
| C-06 | DIFY-ANALYSIS-SUMMARY: "NYQST's current 2-node graph cannot model [Superagent's complexity]" (Section 6.3) — therefore recommends either LangGraph expansion OR focusing on MCP-native tool exposure | COMPARISON-CHECKPOINT: The strategy is NOT ambiguous — DEC-012, DEC-013 lock LangGraph extension with Send() fan-out | DIFY frames an already-decided question as open | DEC-012 and DEC-013 are locked. The Dify "clarify the strategy" action item is moot. LangGraph extension is the path. |
| C-07 | CODEX-ANALYSIS-SUMMARY: Timeline 24 weeks for v1 scope (Section 2.2) | OUR-ANALYSIS-SUMMARY and COMPARISON-CHECKPOINT: 13 weeks, accounting for existing capabilities | 2x divergence on timeline | COMPARISON-CHECKPOINT arbitrated correctly: Codex timeline includes deferred features (browser-use Phase 6) and treats existing capabilities as greenfield. 13 weeks is the correct estimate. |
| C-08 | DIFY-ANALYSIS-SUMMARY: Does NOT mention Langfuse at all for observability; discusses Dify's self-hosted observability patterns | LANGSMITH-COST-EVAL-RESEARCH: Recommends "Langfuse self-hosted" explicitly and definitively | No direct contradiction, but DIFY analysis omits the observability discussion entirely, creating a gap if used in isolation | Not a contradiction — a gap. Langfuse is the resolved answer (DEC-037). |
| C-09 | DIFY-ANALYSIS-SUMMARY Section 7 (Phase 3, Weeks 9–12): "Clarify orchestration strategy (internal graph expansion vs. external MCP agents)" as a required action | CODEX-ANALYSIS-SUMMARY Section 2.5: Assumes LangGraph is the runtime for orchestration. OUR-ANALYSIS-SUMMARY: Assumes LangGraph extension. | DIFY frames a resolved decision as open | DEC-012 (extend ResearchAssistantGraph), DEC-013 (Send() fan-out) are locked. Internal LangGraph orchestration is the path. MCP remains a tool interface, not a replacement for internal orchestration. |
| C-10 | OUR-ANALYSIS-SUMMARY "Most Confident Findings" #4: describes "4-node LangGraph" | All other documents, including OUR-ANALYSIS-SUMMARY Doc 4 body text itself: describe "3-node graph" | Internal inconsistency within OUR-ANALYSIS-SUMMARY | 3-node graph is correct (Ground Truth confirmed). The "4-node" in the confidence table is a counting error — likely counting START as a node, or confusing the 4-step chain description with node count. |

---

## Section 3: Research Findings vs. Earlier Analysis

### 3.1 Langfuse vs. DECISION-REGISTER DEC-037

**LANGSMITH-COST-EVAL-RESEARCH conclusion**: "Langfuse self-hosted is the recommended path" — covers all 5 requirements, MIT-licensed, free to self-host.

**DEC-037**: "Analytics/observability: Use existing Langfuse (not PostHog)" — LOCKED.

**Verdict**: ALIGNED. The research recommendation matches the locked decision. No contradiction.

**One sub-issue**: Section 8.3 of LANGSMITH-COST-EVAL-RESEARCH contains code using `langsmith.Client()` for writing evaluation feedback scores. This is the LangSmith SDK, not Langfuse. The section is framed as "automated quality eval" but uses the wrong client for our locked configuration. A plan restructure agent reading this section could incorrectly conclude that LangSmith is required for eval feedback.

**Correction needed**: The eval feedback code in Section 8.3 should be flagged as "LangSmith-only example; for Langfuse, use `langfuse.score()` API instead."

---

### 3.2 GML Rendering: rehype-to-JSX vs. JSON AST (DEC-015 conflict)

**GML-RENDERING-ANALYSIS Section 4, Recommendation**: "Do not implement the JSON AST layer for Phase 1 or 2. Use the rehype-to-JSX approach."

The rationale given:
- Direct rehype-to-JSX is the proven approach (same as Superagent uses)
- JSON AST adds an extra parse pass
- Not necessary for Phase 1 or 2
- "Revisit the AST layer in Phase 3 if a PDF export or multi-renderer requirement materialises"

**DEC-015 (LOCKED)**: "Markup format: JSON AST (NYQST Markup AST), not raw HTML tags — Easier to validate, heal, render across targets, and export to different formats"

**Verdict**: DIRECT CONFLICT. DEC-015 mandates JSON AST as the locked markup format. GML-RENDERING-ANALYSIS recommends skipping the JSON AST layer and using rehype-to-JSX directly. These are mutually exclusive rendering strategies.

**Analysis of the conflict**: DEC-015 appears to have been written about the OUTPUT format of the LLM (what GML string structure the LLM emits), while GML-RENDERING-ANALYSIS Section 4 is about the INTERNAL rendering pipeline (how the frontend processes that GML string). The confusion is whether "JSON AST" refers to:
- (A) The serialisation format the LLM emits (JSON-encoded GML nodes instead of raw HTML-like tags), OR
- (B) An internal AST object used by the renderer between parsing and React rendering

If DEC-015 means (A) — the LLM emits JSON instead of HTML-like GML tags — then GML-RENDERING-ANALYSIS is talking about a different layer (the renderer internals) and there is no conflict.

If DEC-015 means (B) — there should be an intermediate typed AST before rendering — then GML-RENDERING-ANALYSIS directly contradicts it by recommending to skip that layer.

**REF-013 (Mapping 02)** uses language like "NYQST Markup AST node types (18)" which suggests DEC-015 is about an intermediate AST representation of the markup content — interpretation (B). This makes the conflict real and unresolved.

**This must be explicitly resolved by the plan restructure agent.**

---

### 3.3 Graph Editor: No OSS editor for Send() — does any doc assume a visual editor?

**GRAPH-EDITOR-RESEARCH conclusion**: "No OSS tool supports Send() fan-out editing. The graph must be hand-authored." Recommends: LangSmith Studio for debugging, Langfuse for observability, `get_graph().draw_mermaid()` for graph visualisation in the UI.

**Other docs**: None of the other analysis documents assume a visual graph editor exists or will be built. CODEX-ANALYSIS-SUMMARY lists "orchestration runtime: LangGraph" without specifying a visual editor. OUR-ANALYSIS-SUMMARY discusses the graph in code terms only.

**Verdict**: No conflict. The GRAPH-EDITOR-RESEARCH finding is consistent with all other documents. No doc assumes a visual editor.

**One cross-reference note**: GRAPH-EDITOR-RESEARCH recommends Langfuse for self-hosted observability (aligned with DEC-037 and LANGSMITH-COST-EVAL-RESEARCH). This three-way alignment (DEC-037, LANGSMITH-COST-EVAL-RESEARCH, GRAPH-EDITOR-RESEARCH) is strong.

---

### 3.4 Brave API direct integration vs. MCP-based

**DECISION-REGISTER DEC-032**: "Web search: Brave Search API — direct API integration"

**CODEX-ANALYSIS-SUMMARY Section 3.2**: Lists "Web search" as "Unresolved" with "Which provider(s): Brave/SerpAPI/custom?"

**OUR-ANALYSIS-SUMMARY**: Lists "9+ external data providers (Brave, Firecrawl, Polygon, Crunchbase...)" without specifying whether Brave is direct API or MCP-wrapped.

**GRAPH-EDITOR-RESEARCH**: Mentions "langchain-mcp-adapters" for using MCP tool servers within LangGraph agents. Does not specifically address web search provider.

**None of the docs describe MCP-based web search specifically.** DEC-032 locks Brave Search API (direct API). The COMPARISON-CHECKPOINT notes DEC-032 exists but does not flag Codex's "Unresolved" as stale.

**Verdict**: No doc explicitly contradicts DEC-032. Codex's "Unresolved" is just stale — the decision is made. No MCP-based search integration is mentioned anywhere.

---

## Section 4: Naming and Terminology Consistency

| Item | Issue | Docs Affected | Resolution |
|------|-------|---------------|-----------|
| Chart library naming | CODEX-ANALYSIS-SUMMARY Section 2.4 refers to the recommendation as using Vercel AI SDK (correct) but does not name chart libraries. OUR-ANALYSIS-SUMMARY Doc 3 lists "chart library list (Plotly, Recharts, Lottie, GSAP)" as a mixed set. GML-RENDERING-ANALYSIS consistently uses "react-plotly.js / plotly.js-basic-dist-min" for chart rendering. | OUR-ANALYSIS-SUMMARY, GML-RENDERING-ANALYSIS | GML-RENDERING-ANALYSIS is authoritative for implementation. "Plotly" and "react-plotly.js" refer to the same library. "Recharts" appears in OUR-ANALYSIS-SUMMARY as a reference to Superagent's export UI (separate from the GML renderer), not for our implementation. Recharts is not used in our GML renderer — only Plotly. A plan restructure agent must not conflate these. |
| "Recharts" | OUR-ANALYSIS-SUMMARY Doc 3 mentions "Multi-path rendering (chat UI via Plotly + GML healer, export UI via v0.app + Recharts/D3)" — this is describing Superagent's architecture, not our implementation. | OUR-ANALYSIS-SUMMARY | For OUR implementation: Plotly only. Recharts is Superagent's technology, not ours. DEC-034 (not replicating v0.app) means the Recharts/D3 export path is not being built. |
| Backlog item IDs | COMPARISON-CHECKPOINT references "BL-*" items throughout. DECISION-REGISTER references "BL-001–BL-022". These are consistent. | All docs | Consistent. No issue. |
| Phase numbering | CODEX uses Phase 1–6. Our plan uses Phase 0–3. DIFY uses Phase 1–4. COMPARISON-CHECKPOINT clearly documents this discrepancy and resolves it in favour of the 4-phase (0–3) plan. | All docs | Phase 0–3 is the correct structure (COMPARISON-CHECKPOINT arbitration). Codex phases are discarded. Dify phases are incorrect because Phase 1 contains already-completed work. |
| "ResearchAssistantGraph" vs. "research_assistant.py" vs. "3-node graph" | All docs use these interchangeably and correctly to refer to the same object. | All docs | Consistent. No issue. |
| "NYQST Markup v1" vs. "JSON AST" vs. "NYQST Markup AST" | Codex uses "NYQST Markup v1". DEC-015 and REF-013 use "JSON AST (NYQST Markup AST)". GML-RENDERING-ANALYSIS uses "rehype-to-JSX" approach without naming it "NYQST Markup". | CODEX-ANALYSIS-SUMMARY, GML-RENDERING-ANALYSIS, DECISION-REGISTER | The canonical name from the locked decision is "NYQST Markup AST" (DEC-015). The rendering strategy conflict (Section 3.2 above) must be resolved before this naming is meaningful. |
| "LangGraph Studio" vs. "LangSmith Studio" | COMPARISON-CHECKPOINT (date 2026-02-18) refers to "LangGraph Studio". GRAPH-EDITOR-RESEARCH (date 2026-02-19) correctly notes the October 2025 rename: "LangGraph Studio → LangSmith Studio". | ANALYSIS-COMPARISON-CHECKPOINT | GRAPH-EDITOR-RESEARCH is more current. The correct name is "LangSmith Studio". This is a branding change with no functional impact — but a plan restructure agent should use the current name. |
| "arq" background jobs | PLATFORM-GROUND-TRUTH: "arq>=0.26.0 + redis wired but background job definitions in jobs.py". COMPARISON-CHECKPOINT: "arq background workers are wired (async entity creation is infrastructure-ready)". DECISION-REGISTER DEC-017: "Async entity creation: Decoupled from main response stream via arq background worker" (LOCKED). | All | Consistent naming. "arq" is the correct term throughout. |
| "Send()" pattern capitalization | DIFY-ANALYSIS-SUMMARY: "Send()" (correct). OUR-ANALYSIS-SUMMARY: "Send()" (correct). COMPARISON-CHECKPOINT: "Send()" (correct). GRAPH-EDITOR-RESEARCH: "Send()" (correct). LANGSMITH-COST-EVAL-RESEARCH: uses `Send` in code examples (correct Python). PLATFORM-GROUND-TRUTH: "No `Send(` pattern found" (consistent with the established usage in all docs). | All | Consistent. |

---

## Section 5: Recommendations Alignment

### 5.1 Observability / Cost Tracking

| Doc | Recommendation |
|-----|---------------|
| LANGSMITH-COST-EVAL-RESEARCH | Langfuse self-hosted (primary); LangSmith optional for eval-only use |
| GRAPH-EDITOR-RESEARCH | Langfuse (MIT, Docker Compose) — aligned |
| CODEX-ANALYSIS-SUMMARY | Lists "Langfuse vs LangSmith vs OpenTelemetry-first" as Unresolved |
| DIFY-ANALYSIS-SUMMARY | Does not address observability tooling |
| DECISION-REGISTER DEC-037 | Langfuse — LOCKED |

**Verdict**: LANGSMITH-COST-EVAL-RESEARCH and GRAPH-EDITOR-RESEARCH are aligned with DEC-037. CODEX-ANALYSIS-SUMMARY is stale (lists it as unresolved). DIFY-ANALYSIS-SUMMARY is silent. No split recommendation issue — Langfuse is the answer everywhere that has an answer.

**One nuance**: LANGSMITH-COST-EVAL-RESEARCH suggests a "hybrid approach" (Langfuse for production, LangSmith for offline eval) as optional. This is not a contradiction of DEC-037 — it is an additive possibility. DEC-037 says "use Langfuse (not PostHog)" which does not preclude using LangSmith evaluators offline if the team chooses. However, DEC-037's spirit is to avoid vendor proliferation. A plan restructure agent should treat Langfuse as the single observability answer and note that LangSmith's `agentevals` library (which works independently) is an optional add-on.

---

### 5.2 Search Provider

| Doc | Recommendation |
|-----|---------------|
| CODEX-ANALYSIS-SUMMARY | "Unresolved: Brave/SerpAPI/custom?" |
| LANGSMITH-COST-EVAL-RESEARCH | Not addressed |
| GRAPH-EDITOR-RESEARCH | Not addressed |
| DECISION-REGISTER DEC-032 | Brave Search API — LOCKED |

**Verdict**: Codex is stale. DEC-032 resolves this. No split recommendation.

---

### 5.3 GML / Markup Rendering Strategy

| Doc | Recommendation |
|-----|---------------|
| CODEX-ANALYSIS-SUMMARY | "JSON AST (recommended) or HTML-like tag set" — both presented as options |
| GML-RENDERING-ANALYSIS | "Do not implement JSON AST. Use rehype-to-JSX." |
| DECISION-REGISTER DEC-015 | "JSON AST (NYQST Markup AST)" — LOCKED |
| DECISION-REGISTER DEC-040 | "GML healer: Pydantic validator + AST repair logic in Python" — LOCKED |

**Verdict**: THREE-WAY CONFLICT. DEC-015 locks JSON AST. GML-RENDERING-ANALYSIS recommends against it. Codex's "HTML-like tag set" option is also killed by DEC-015. The GML-RENDERING-ANALYSIS was written after DEC-015 was locked (doc date 2026-02-19 vs. DEC-015 date 2026-02-16) and appears unaware of DEC-015 or is intentionally reconsidering it. This is the most significant unresolved conflict in the entire document set.

**Recommended resolution**: See Section 6, Correction C-GML.

---

### 5.4 RAG Quality Improvements

| Doc | Recommendation |
|-----|---------------|
| DIFY-ANALYSIS-SUMMARY | Phase 2 (Weeks 5–8): configurable chunks, reranking (Cohere/Jina), hybrid search, embedding cache — 4–6 weeks |
| CODEX-ANALYSIS-SUMMARY | Not explicitly addressed as a separate phase |
| COMPARISON-CHECKPOINT | Adopt Dify's RAG quality roadmap but reprioritise to Phase 2; verify claims against actual `rag_service.py` before committing |
| OUR-ANALYSIS-SUMMARY | Says RAG is "fully implemented" without quality assessment |

**Verdict**: Aligned in direction (RAG needs quality improvements). The COMPARISON-CHECKPOINT correctly notes that Dify's specific claims (2000-char fixed chunks, no reranking) are plausible but unverified against actual code. Before a plan restructure agent includes RAG improvements in the backlog, `rag_service.py` must be audited to confirm these claims.

---

## Section 6: Corrections the Plan Restructure Agent Must Apply

The following are specific factual corrections that must be baked into the final plan to avoid propagating errors from analysis documents into implementation work.

---

### C-01: Remove all work items assuming conversations/messages tables are missing

**Error source**: DIFY-ANALYSIS-SUMMARY Sections 1.1, 3.1, 6.1, 7 (Phase 1, Weeks 1–4)

**Stale claim**: "Implement conversations + messages tables (2–3 weeks) as the first data model addition"

**Correction**: Migration 0004 already added: `conversations`, `messages`, `message_feedback`, `sessions`, `tags` tables. Full CRUD API at `/api/v1/conversations`. Frontend `conversation-store.ts` (Zustand, persisted). This is DONE. Any backlog item containing language like "add conversation table," "implement message persistence," or "build conversation API" is complete. The Phase 1 slot freed by this correction (2–3 weeks) should be reallocated to fan-out orchestration or GML renderer work.

**Verification action**: Before closing this correction, confirm that the existing conversation API and `conversation-store.ts` satisfy the requirements for `deliverable_type` on user messages (DEC-023) and conversation branching implied by the `parent_message_id` pattern. These may be gaps in the existing implementation even though the tables exist.

---

### C-02: Correct the graph node count — 3 nodes, not 4 and not 2

**Error source**: DIFY-ANALYSIS-SUMMARY "2-node pipeline"; OUR-ANALYSIS-SUMMARY "4-node LangGraph" (confidence table item #4)

**Correct fact**: ResearchAssistantGraph is a **3-node** StateGraph: `agent`, `tools` (ToolNode), `capture_sources`. Entry point is `agent`. Conditional edges: agent → tools (if tool call) or agent → END (if done). tools → capture_sources → agent (loop back).

**Tools in ToolNode**: `search_documents`, `list_notebooks`, `get_document_info`, `compare_manifests` (4 tools, confirmed Ground Truth).

**Implication**: The graph is not a "2-node retrieve→generate pipeline" (Dify is wrong — it underestimates existing capability). The graph is not 4 nodes (OUR-ANALYSIS is a counting error). The correct baseline for "extend this graph" is 3 nodes + conditional edge loop.

---

### C-03: Remove "NYQST is a prototype" framing from any plan narrative

**Error source**: DIFY-ANALYSIS-SUMMARY Executive Summary, Conclusion

**Stale claim**: "NYQST is an early-stage prototype" vs. "Dify is mature, production-grade"

**Correction**: NYQST is a functioning platform with: 16 tables, 11 API routers, full JWT + API key auth with multi-tenant scoping and rate limiting, working LangGraph agent with tool loop, SSE streaming via PG LISTEN/NOTIFY, MCP server with substrate/knowledge/run tools, and a React frontend with chat, citations, run timeline, workbench, and conversation persistence. It is not feature-complete for Superagent parity, but it is not a prototype. Any plan narrative that describes the platform as early-stage is incorrect and will lead to inflated effort estimates.

---

### C-04: Resolve the GML rendering strategy conflict (DEC-015 vs. GML-RENDERING-ANALYSIS)

**Error source**: Conflict between DEC-015 (locked) and GML-RENDERING-ANALYSIS Section 4 recommendation

**The conflict**:
- DEC-015 locks "JSON AST (NYQST Markup AST)" as the markup format
- GML-RENDERING-ANALYSIS Section 4 recommends "Do not implement the JSON AST layer for Phase 1 or 2. Use rehype-to-JSX."

**Possible interpretations**:
- (A) DEC-015 refers to the LLM OUTPUT format (LLM emits JSON-encoded AST nodes instead of raw HTML-like tag strings). GML-RENDERING-ANALYSIS refers to the RENDERER INTERNALS (how the frontend processes what it receives). No conflict — they are about different layers.
- (B) DEC-015 refers to an intermediate typed AST in the renderer. GML-RENDERING-ANALYSIS contradicts it by recommending direct rehype-to-JSX without an intermediate AST.

**Evidence for interpretation (A)**: REF-013 (Mapping 02) uses "NYQST Markup AST node types (18)" in the context of defining the deliverable artifact format stored as a Manifest, not the renderer internals.

**Evidence for interpretation (B)**: GML-RENDERING-ANALYSIS Section 4 explicitly discusses "the GML string is first parsed to a typed JSON AST, and React components consume the AST" as the alternative it is recommending against, suggesting the question is about renderer internals.

**Required action**: The plan restructure agent must explicitly resolve this by clarifying what layer DEC-015 applies to. If DEC-015 is about LLM output format (layer A), the GML-RENDERING-ANALYSIS renderer approach (rehype-to-JSX) is acceptable and there is no conflict. If DEC-015 is about renderer internals (layer B), GML-RENDERING-ANALYSIS's recommendation contradicts a locked decision and must be overridden.

**Recommended resolution (pending user confirmation)**: DEC-015 most likely refers to the LLM OUTPUT FORMAT — the LLM is instructed to emit NYQST Markup in JSON AST form rather than raw HTML-like strings. The frontend renderer then processes that JSON AST. This means: (1) the LLM produces a JSON-encoded GML document, (2) the renderer reads the JSON AST directly rather than parsing HTML strings, (3) rehype is NOT needed because the input is already structured JSON, not HTML. If this is the correct interpretation, GML-RENDERING-ANALYSIS's extensive use of rehype-parse and unified is architecturally misaligned with DEC-015 and the whole renderer section needs to be redesigned for JSON input.

---

### C-05: Mark all Codex "Unresolved" items as resolved where applicable

**Error source**: CODEX-ANALYSIS-SUMMARY Section 3.2 infrastructure matrix

**Stale "Unresolved" items with locked resolutions**:

| Codex "Unresolved" | Resolution |
|--------------------|-----------|
| Auth: "Supabase/Auth0/Ory/custom? SSO?" | DEC-038: Use existing intelli auth (JWT + API keys). LOCKED. |
| Web search: "Brave/SerpAPI/custom?" | DEC-032: Brave Search API. LOCKED. |
| Crawl/extract: "Firecrawl/custom crawler?" | DEC-033: Jina Reader API. LOCKED. |
| Browser automation | DEC-002: Deferred to v2. LOCKED. |
| Streaming protocol: "dual SSE vs NDJSON?" | DEC-020, DEC-021: AI SDK SSE + PG LISTEN/NOTIFY SSE. LOCKED. |
| Observability: "Langfuse vs LangSmith vs OTel-first?" | DEC-037: Langfuse. LOCKED. |
| Analytics/flags | DEC-064: Use existing Langfuse (not PostHog). LOCKED. |
| Object storage | MinIO in dev (S3-compatible) — existing infrastructure, no change needed. |
| Deploy target for websites | DEC-035: iframe preview only in v1. LOCKED. |

**Items still unresolved from Codex matrix**: Model provider (OQ-001: still open), Vector/search backend (not in DEC register — pgvector default, OpenSearch optional), "Pro sources" premium connectors (out of scope for v1), Deployment/containerization (no Dockerfile exists — genuine gap, no locked decision).

---

### C-06: Correct Codex timeline — do not use 24-week estimate

**Error source**: CODEX-ANALYSIS-SUMMARY Section 2.2 (6 phases, ~24 weeks)

**Correction**: The 24-week Codex estimate is invalid because:
1. Phase 6 (browser-use/HITL, 6–12 weeks) is explicitly deferred to v2 by DEC-002.
2. Phase 2 (Entity & citation substrate, 2–4 weeks) is collapsed to a migration + API field addition by DEC-016.
3. Existing conversations/sessions/messages reduce Phase 1 scope by 2–3 weeks.
4. Auth is complete — no auth work needed.

**Correct estimate**: 13 weeks (4 phases: 0, 1, 2, 3) per OUR-ANALYSIS-SUMMARY and COMPARISON-CHECKPOINT. This may be slightly optimistic but is grounded in the actual codebase.

---

### C-07: LangSmith Studio is the current name; LangGraph Studio is deprecated branding

**Error source**: COMPARISON-CHECKPOINT uses "LangGraph Studio" (written 2026-02-18)

**Correction**: As of October 2025, LangChain renamed: LangGraph Studio → LangSmith Studio. GRAPH-EDITOR-RESEARCH (2026-02-19) has the correct current name. The functionality is unchanged. Any implementation plan referencing "LangGraph Studio" should be updated to "LangSmith Studio."

---

### C-08: Langfuse eval feedback code must not use LangSmith SDK

**Error source**: LANGSMITH-COST-EVAL-RESEARCH Section 8.3

**Stale claim**: Section 8.3 ("Automated Quality Eval After Each Run") uses `ls_client = Client()` from `langsmith` to attach feedback scores via `ls_client.create_feedback()`.

**Correction**: DEC-037 locks Langfuse as the observability tool. In a Langfuse-only setup (no LangSmith), the feedback attachment must use Langfuse's API:
```python
langfuse.score(
    trace_id=run_id,
    name="quality_score",
    value=result.score / 5,
    comment=result.reasoning
)
```
The LangSmith SDK code in Section 8.3 is not usable without a LangSmith subscription. Mark it as "LangSmith-variant" and provide the Langfuse equivalent in the implementation plan.

**Note**: The broader recommendation of LANGSMITH-COST-EVAL-RESEARCH (Langfuse self-hosted) is correct and aligned with DEC-037. Only Section 8.3's code example is wrong for our configuration.

---

### C-09: The `<answer>` wrapper is not mentioned in GML-RENDERING-ANALYSIS — it must be

**Error source**: GML-RENDERING-ANALYSIS (omission)

**Missing fact**: DEC-022 locks the response format as `<answer>...</answer>` wrapper with `<gml-*>` tags inside. The GML renderer must strip the `<answer>` wrapper before processing the GML content. GML-RENDERING-ANALYSIS does not mention the `<answer>` wrapper anywhere in its parsing pipeline, rendering patterns, or implementation checklist.

**Correction**: Add to the GML-RENDERING-ANALYSIS implementation checklist (Section 7):
- "Extract GML content from `<answer>...</answer>` wrapper before passing to `GmlRenderer`"
- The extractor should handle: partial `<answer>` during streaming (buffer until closing tag), malformed wrapper (fallback to plain markdown rendering), and nested tags within the answer.

This is not a renderer concern per se — it is a stream event handler concern. But GML-RENDERING-ANALYSIS does not reference where this unwrapping happens, leaving a gap in the implementation spec.

---

### C-10: DIFY Phase 3 "clarify orchestration strategy" action is moot — delete it

**Error source**: DIFY-ANALYSIS-SUMMARY Section 7, Phase 3 (Weeks 9–12)

**Stale item**: "Clarify orchestration strategy (internal graph expansion vs. external MCP agents)"

**Correction**: DEC-012 (extend ResearchAssistantGraph) and DEC-013 (Send() fan-out) are locked. The orchestration strategy is internal LangGraph expansion. This is not a question to be "clarified" — it is decided. Any plan that includes a Phase 3 item to "decide" this will waste time on a non-question.

**What replaces it**: The actual Phase 3 work is deliverable generation (report, website, slides, document pipelines) per DEC-001 and the backlog items in BACKLOG.md.

---

## Section 7: Summary of Issue Severity

| ID | Severity | Status | Description |
|----|----------|--------|-------------|
| C-01 | CRITICAL | Not in CHECKPOINT | DIFY Phase 1 work (conversation persistence) already done — must be removed from plan |
| C-02 | HIGH | In CHECKPOINT | Graph is 3 nodes, not 2 (Dify) or 4 (Our Analysis typo) |
| C-03 | MEDIUM | In CHECKPOINT | NYQST is not a prototype — remove that framing |
| C-04 | HIGH | NOT in CHECKPOINT | GML rendering strategy conflicts with DEC-015 — requires explicit resolution |
| C-05 | MEDIUM | In CHECKPOINT | Codex "Unresolved" items are resolved — mark them closed |
| C-06 | MEDIUM | In CHECKPOINT | Codex 24-week timeline is 2x too long |
| C-07 | LOW | NOT in CHECKPOINT | LangSmith Studio is the current name (was LangGraph Studio) |
| C-08 | LOW | NOT in CHECKPOINT | Section 8.3 eval code uses LangSmith SDK, not Langfuse SDK |
| C-09 | MEDIUM | NOT in CHECKPOINT | GML renderer does not address `<answer>` wrapper stripping (DEC-022) |
| C-10 | MEDIUM | In CHECKPOINT | DIFY Phase 3 "clarify orchestration" is moot — strategy is locked |
| C-11 | HIGH | NOT in CHECKPOINT | GML-RENDERING-ANALYSIS recommends "skip JSON AST" which may contradict DEC-015 |
| C-12 | LOW | NOT in CHECKPOINT | "Recharts" in OUR-ANALYSIS describes Superagent's tech, not ours — Plotly only for our impl |
| C-13 | LOW | NOT in CHECKPOINT | DIFY "clarify MCP vs. internal orchestration" framing is stale — internal LangGraph is decided |

---

## Section 8: Items Correctly Handled by COMPARISON-CHECKPOINT

The following significant contradictions were already correctly identified and arbitrated in COMPARISON-CHECKPOINT. No further action needed — they are captured:

1. Conversation persistence: Dify wrong, migration 0004 exists
2. Graph node count: Dify wrong (2 nodes), 3 nodes confirmed
3. Table count: Dify wrong (11), 16 tables confirmed
4. RAG capability: Dify gets platform facts wrong but quality recommendations are sound
5. SSE event count: conflation of AI SDK stream vs. platform RunEventType enum
6. LangGraph checkpointing: wired but not exercised in production UX
7. Timeline: Codex 24wk too long; 13wk is realistic
8. NYQST "prototype" framing: incorrect, it's a functioning platform
9. LLM is OpenAI-only (no Anthropic SDK)
10. Billing is greenfield but data model (cost_cents, token_usage) is ready

---

**Generated:** 2026-02-19
**Auditor:** Claude Sonnet 4.6 (claude-sonnet-4-6)
**Method:** Full read of all 8 analysis documents + DECISION-REGISTER.md, cross-referenced for factual contradictions, stale claims, and alignment gaps. Authority ranking followed COMPARISON-CHECKPOINT: PLATFORM-GROUND-TRUTH > OUR-ANALYSIS > DIFY-ANALYSIS > CODEX-ANALYSIS, with DECISION-REGISTER as the definitive arbiter of locked decisions.
