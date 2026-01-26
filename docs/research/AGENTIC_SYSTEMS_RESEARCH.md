# Agentic Systems Research Synthesis

**Date:** January 2026
**Purpose:** Research findings from key players in agentic systems to inform NYQST PRD and ADR decisions.

---

## 1. Anthropic - Building Effective Agents

**Source:** https://www.anthropic.com/research/building-effective-agents

### Key Architectural Distinction

Anthropic draws a critical distinction between **Workflows** and **Agents**:

- **Workflows**: Systems where LLMs and tools are orchestrated through **predefined code paths**. Deterministic, auditable, predictable.
- **Agents**: Systems where LLMs **dynamically direct their own processes** and tool usage, maintaining control over how they accomplish tasks.

> **NYQST Implication:** This maps directly to our Task vs Workflow distinction. Tasks are agent-directed (flexible), Workflows are predefined (governed). Our Camunda integration should handle the Workflow side.

### Design Principles

1. **Start Simple**: "Find the simplest solution possible, and only increase complexity when needed. This might mean not building agentic systems at all."

2. **Composable Patterns**: The most successful implementations use simple, composable patterns rather than complex frameworks.

3. **When NOT to use agents**: Agentic systems often trade latency and cost for better task performance. Only use when the tradeoff is worth it.

### Long-Running Agent Patterns

From "Effective harnesses for long-running agents" (Nov 2025):

- **Core Challenge**: Agents must work in discrete sessions, each new session begins with no memory of what came before.
- **Solution**: Two-fold approach:
  1. **Initializer Agent**: Sets up the environment on first run
  2. **Coding Agent**: Makes incremental progress in every session, leaving clear artifacts for the next session

> **NYQST Implication:** Our Session/VM architecture should support this pattern. Sessions need state persistence and clear handoff artifacts.

### Tool Design Principles

From "Writing effective tools for AI agents" (Sep 2025):

1. **Namespacing**: Define clear boundaries in functionality
2. **Meaningful Context**: Return meaningful context from tools back to agents
3. **Token Efficiency**: Optimize tool responses for token efficiency
4. **Good Descriptions**: Prompt-engineer tool descriptions and specs

> **NYQST Implication:** Our Skills system should follow these principles. Skills need clear namespacing, efficient responses, and well-documented interfaces.

### Agent Evaluation

From "Demystifying evals for AI agents" (Jan 2026):

- Single-turn evaluations are insufficient for agents
- **Multi-turn evaluations** are essential: prompt, multiple tool calls, state modifications, grading logic
- Evaluations should measure what matters for production, not just accuracy

> **NYQST Implication:** Our testing and validation approach needs multi-turn evaluation capabilities. ADR needed for evaluation framework.

---

## 2. LangGraph - State Machine Orchestration

**Source:** DeepWiki analysis of langchain-ai/langgraph

### Core Concepts

LangGraph is "a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents."

**Key Capabilities:**
- **Durable Execution**: Agents persist through failures and resume from interruption points
- **Human-in-the-Loop**: State inspection and modification at any workflow stage
- **Checkpointing**: State persistence across context windows

### Architecture Components

1. **StateGraph API**: Define nodes and edges as a graph
2. **Functional API**: `@task` and `@entrypoint` decorators for simpler patterns
3. **Pregel Execution Engine**: Handles graph execution
4. **Channels**: State management primitives
5. **Interrupts**: Human-in-the-loop control points

### Checkpointing Architecture

- **MemorySaver**: In-memory only (for development)
- **SqliteSaver**: SQLite-based persistence
- **PostgresSaver**: Production-grade persistence
- **Time Travel**: Ability to fork and replay from any checkpoint

> **NYQST Implication:** Our session persistence should support similar checkpointing. Consider LangGraph as potential orchestration layer or build similar capabilities.

### Human-in-the-Loop Patterns

- **Interrupts**: Pause execution at specific nodes
- **State Inspection**: View and modify state before resuming
- **Approval Gates**: Require human approval before proceeding

> **NYQST Implication:** Critical for our governed workflows. Camunda integration should support these patterns.

### Prebuilt Components

- **ReAct Agent**: `create_react_agent()` - Reasoning + Acting pattern
- **ToolNode**: Standardized tool execution
- **UI Integration**: Streaming and state synchronization

---

## 3. Vercel AI SDK 6

**Source:** https://vercel.com/blog/ai-sdk-6

### Key Features (Dec 2025)

1. **Agents**: First-class agent support
2. **Tool Execution Approval**: Human-in-the-loop for tool calls
3. **DevTools**: Debugging and inspection
4. **Full MCP Support**: Model Context Protocol integration
5. **Streaming**: Real-time response streaming
6. **Provider Agnostic**: Switch models with minimal code changes

### Agent Architecture

```typescript
const agent = createAgent({
  model: 'openai/gpt-4',
  tools: [...],
  onToolCall: async (toolCall) => {
    // Approval logic
  }
});
```

### Real-World Usage

- **Thomson Reuters CoCounsel**: Built with 3 developers in 2 months, serving 1,300 accounting firms
- **Clay Claygent**: AI web research agent at massive scale

> **NYQST Implication:** Consider Vercel AI SDK for TypeScript-based agent implementation. Good patterns for tool approval and streaming.

---

## 4. CopilotKit - Generative UI

**Source:** DeepWiki analysis of CopilotKit/CopilotKit

### What is Generative UI?

"Any user interface that is partially or fully produced by an AI agent, rather than authored exclusively by human designers and developers."

### Application Surfaces

1. **Chat (Threaded Interaction)**: Slack-like conversational interface
2. **Application (Embedded)**: UI components embedded in the application

### Key Hooks

1. **useAgent**: Agent state management
2. **useCopilotChat**: Chat interaction
3. **useFrontendTool**: Define tools callable from frontend
4. **useHumanInTheLoop**: Human approval patterns
5. **useRenderToolCall**: Custom tool call rendering
6. **useCoAgentStateRender**: Render agent state

### AG-UI Protocol

Agent-to-User Interface protocol for standardized agent-UI communication:
- Event streaming
- State synchronization
- Tool call rendering

### Generative UI Types

1. **Static Components**: Pre-built components rendered by agent
2. **Dynamic Components**: Components generated at runtime
3. **Hybrid**: Combination of static and dynamic

> **NYQST Implication:** Our Dynamic Views (Day 2) should follow similar patterns. CopilotKit provides good reference for guardrailed app generation.

---

## 5. Document Processing Tools

### Docling (IBM)

**Source:** https://www.ibm.com/new/announcements/granite-docling-end-to-end-document-conversion

**Granite-Docling-258M** (Sep 2025):
- Ultra-compact 258M parameter VLM
- Apache 2.0 license
- 97.9% table cell accuracy (benchmark leader)
- Handles: inline/floating math, code, table structure, layout preservation
- Output: DocTags format (preserves connection to source content)

**Key Differentiators:**
- Single model for end-to-end processing
- Faithful translation of complex structural elements
- Ideal for downstream RAG applications
- Local execution for sensitive data

### LlamaParse v2

**Source:** https://www.llamaindex.ai/blog/introducing-llamaparse-v2-simpler-better-cheaper

**Tiers** (Dec 2025):
- Parse without AI (fast, cheap)
- Parse with LLM (text understanding)
- Parse with LVM (vision understanding)
- Parse with Agent (complex documents)

**Multimodal Parsing:**
- Screenshot every page
- Send to multimodal model
- Extract as markdown
- Consolidate results

**Speed:** ~6 seconds per document regardless of size

### Unstructured.io

**Source:** https://unstructured.io/blog/new-white-paper-fueling-the-agentic-enterprise

**SCORE Framework** (Dec 2025):
- Structural and Content Robust Evaluation
- Purpose-built for generative era
- Handles semantically identical but structurally different outputs

**Key Capabilities:**
- 70+ document types
- DAG-based workflows
- Smart chunking
- Embedding integrations
- Enterprise-grade security

**"Agent-Ready" Data Architecture:**
- Vision-Language Models replacing traditional OCR
- 80-90% of enterprise data is "dark data"
- 70-85% of failed AI initiatives trace to data architecture issues

> **NYQST Implication:** ADR needed for document processing pipeline. Consider Docling for accuracy, LlamaParse for speed, Unstructured for enterprise features. SCORE framework relevant for our evaluation approach.

---

## 6. Google Antigravity

**Source:** https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/

### Agent-First IDE (Nov 2025)

**Two Interfaces:**
1. **Editor View**: Hands-on, AI-powered IDE with tab completions and inline commands
2. **Manager Surface**: Dedicated interface to spawn, orchestrate, and observe multiple agents

### Key Concepts

- **Cross-Surface Agents**: Synchronized control across editor, terminal, and browser
- **Task-Oriented Abstraction**: Work at higher level than line-by-line coding
- **Artifact-Based Transparency**: See what agents produce
- **Persistent Knowledge**: Context preserved across sessions

### Use Cases

1. Delegate complex, multi-tool software tasks to agents
2. Agent autonomously plans and executes across editor, terminal, browser
3. Multiple agents working in parallel across workspaces

> **NYQST Implication:** Our session/workspace architecture should support similar patterns. The Manager Surface concept aligns with our Background Copilot vision.

---

## 7. Key Patterns and ADR Recommendations

### ADR: Agent Framework Choice

**Options:**
1. LangGraph (Python, mature, checkpointing)
2. Vercel AI SDK (TypeScript, streaming, MCP)
3. Custom (full control, more work)

**Recommendation:** Hybrid - LangGraph for complex workflows, Vercel AI SDK for frontend integration.

### ADR: Document Processing Pipeline

**Options:**
1. Docling (accuracy, local, open source)
2. LlamaParse (speed, multimodal, cloud)
3. Unstructured (enterprise, DAG workflows)
4. Hybrid pipeline

**Recommendation:** Docling as primary (accuracy + local execution), LlamaParse for speed-critical paths.

### ADR: Generative UI Framework

**Options:**
1. CopilotKit (React, AG-UI protocol, mature)
2. Custom (full control)
3. Vercel AI SDK UI components

**Recommendation:** CopilotKit patterns for reference, custom implementation for guardrailed app generation.

### ADR: State Management / Checkpointing

**Options:**
1. LangGraph checkpointers
2. Custom PostgreSQL-based
3. Redis-based

**Recommendation:** PostgreSQL-based (aligns with existing stack), with LangGraph-compatible interface.

### ADR: Evaluation Framework

**Options:**
1. SCORE framework (Unstructured)
2. Custom multi-turn evaluation
3. LangSmith integration

**Recommendation:** Custom framework inspired by SCORE, with multi-turn evaluation capabilities.

### ADR: MCP Architecture

**Options:**
1. Full MCP adoption (all services as MCP)
2. Selective MCP (external services only)
3. MCP + internal API hybrid

**Recommendation:** MCP for external/sellable services, internal API for core platform.

---

## 8. PRD Updates Completed

Based on this research, the following PRD sections have been updated:

### 03_PLATFORM.md Updates:
- **Workflow vs Agent Distinction** (lines 290-298): Added Anthropic's architectural pattern distinguishing predefined workflows from dynamic agents
- **Long-Running Agent Patterns** (lines 300-310): Added Initializer Agent and Incremental Progress Agent patterns for session bridging
- **Tool Design Principles** (lines 321-333): Added namespacing, meaningful context, token efficiency, and description standards
- **Document Processing Pipeline** (lines 365-389): Added multi-tier approach (Fast/LLM/Vision/Agent Parse) with SCORE evaluation framework

### 06_ARCHITECTURE.md Updates:
- **Checkpointing Architecture** (lines 248-263): Added storage tiers (Memory/SQLite/PostgreSQL), granularity policies, and state recovery patterns
- **Human-in-the-Loop Patterns** (lines 265-279): Added interrupt points, state inspection, approval gates, feedback integration, and edit-and-continue
- **Generative UI Architecture** (lines 710-738): Added AG-UI protocol, two surfaces (Chat/Application), agent-generated components, streaming updates, and guardrails

### New ADR Notes Added:
- **Long-Running Agent Patterns** (03_PLATFORM.md): Initializer vs progress agent, artifact format, checkpoint granularity
- **Tool Design Standards** (03_PLATFORM.md): Skill interface specification, namespacing, response format
- **Document Processing Pipeline** (03_PLATFORM.md): Tier selection, parser technology, evaluation metrics
- **Checkpointing Architecture** (06_ARCHITECTURE.md): Storage backend, granularity policies, serialization, pruning
- **Human-in-the-Loop Patterns** (06_ARCHITECTURE.md): Interrupt triggers, state inspection, approval workflow, feedback
- **Generative UI Architecture** (06_ARCHITECTURE.md): Component library, AG-UI protocol, state sync, guardrails
- **Agent Framework Choice** (06_ARCHITECTURE.md): LangGraph vs Vercel AI SDK vs custom
- **MCP Architecture** (06_ARCHITECTURE.md): Full adoption vs selective, tool design, workflow in MCP

---

## References

1. Anthropic - Building Effective Agents (Dec 2024)
2. Anthropic - Demystifying evals for AI agents (Jan 2026)
3. Anthropic - Writing effective tools for agents (Sep 2025)
4. Anthropic - Effective harnesses for long-running agents (Nov 2025)
5. LangGraph Documentation and DeepWiki Analysis
6. Vercel AI SDK 6 Announcement (Dec 2025)
7. CopilotKit Documentation and DeepWiki Analysis
8. IBM Granite-Docling Announcement (Sep 2025)
9. LlamaParse v2 Announcement (Dec 2025)
10. Unstructured.io - Fueling the Agentic Enterprise (Jan 2026)
11. Google Antigravity Announcement (Nov 2025)
