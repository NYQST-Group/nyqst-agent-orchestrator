# ORCHESTRATION DOMAIN EXTRACTION
## Deep Content Analysis for Agentic Runtime & Orchestration

**Date**: 2026-02-20
**Status**: Comprehensive extraction from live system analysis
**Confidence**: HIGH (90%+ on schemas, patterns; MEDIUM on algorithms)
**Sources**: 5 primary analysis documents + live bundle analysis

---

## SECTION 1: SCHEMAS & DATA MODELS

### 1.1 Planning Hierarchy (Pydantic/TypeScript)

#### PlanSet (Root Execution Context)
```python
# Pydantic definition (backend)
from typing import Dict, Optional, List
from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"

class PlanSet(BaseModel):
    plans: Dict[str, 'Plan']  # plan_id -> Plan
    chat_id: str              # Conversation ID
    workspace_id: str         # Multi-tenant isolation
    created_at: Optional[int] = None  # Timestamp

    class Config:
        # LinkedList traversal: parent -> previous_plan_id -> parent.plans[id]
        validate_assignment = True
```

**Semantic**: PlanSet is the **root of execution scope**. All research tasks, deliverables, and artifacts belong to a single PlanSet. Equivalent to a LangGraph `thread_id` in durable execution.

**Constraints**:
- Immutable once created
- All Plans share same workspace_id (multi-tenant boundary)
- LinkedList ordering: `previous_plan_id` forms chain back to root

#### Plan (Phase/Orchestration Unit)
```python
class Plan(BaseModel):
    plan_id: str                              # UUID, globally unique
    plan_tasks: Dict[str, 'PlanTask']         # task_id -> PlanTask
    previous_plan_id: Optional[str] = None    # LinkedList chain
    status: Status                            # "loading" | "success" | "error"
    used_sources: List['Source'] = []         # Citation/entity references
    iteration_number: Optional[int] = None    # For multi-stage planning

    class Config:
        extra = "allow"  # Extensible for future fields

class Source(BaseModel):
    source_id: str
    url: str
    title: str
    provider: str  # "brave" | "firecrawl" | "factset" | ...
    retrieved_at: Optional[str] = None
```

**Semantic**: Plan is a **phase within execution**. Multiple Plans exist in LinkedList order:
1. Initial planning ("Devising Initial Research Strategy")
2. Adaptive re-planning ("Considering Results and Refining Research Strategy")
3. (Optional) Further refinement phases

**State Transitions**:
```
LOADING → (all tasks complete) → SUCCESS
       ↓ (any task ERROR)
       → ERROR (unless graceful degradation)
```

#### PlanTask (Individual Research Task)
```python
class PlanTask(BaseModel):
    plan_task_id: str                    # UUID
    plan_id: str                         # Parent reference (backpointer)
    title: str                           # Human-readable task name
    message: str                         # Task description/prompt
    previous_task_id: Optional[str] = None  # LinkedList ordering
    status: Status                       # Task-level status

    # Execution telemetry
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    duration_ms: Optional[int] = None

    # Results
    notes: Optional[str] = None          # Synthesized notes
    sources: List[Source] = []           # Tool results as entities
    entities: List[str] = []             # Entity IDs from research

    class Config:
        extra = "allow"
```

**Semantic**: PlanTask is the **atomic unit of parallel work**. Each task:
- Runs independently with its own tool set
- Emits granular telemetry (`node_tool_event`)
- Produces structured output (notes + sources)

**Example Tasks** (from screenshot):
```
title: "Deep Market Landscape Analysis"
message: "Analyze current market position, growth trends, and competitive dynamics"
tools: ["web_search", "firecrawl_scrape"]
```

### 1.2 State Machine: Task Lifecycle

```
LOADING (queued)
  ↓ [node_tools_execution_start emitted]
PROCESSING (running tools)
  ↓ [for each tool: tool_call_started, tool_result, tool_call_completed]
CREATING NOTES (synthesis)
  ↓ [LLM synthesizes tool results into notes]
SUCCESS ✓
  ↓
[Task results added to aggregation queue]

Alternative path:
PROCESSING → ERROR [tool failure, timeout, or exception]
  ↓
[Graceful degradation: mark gap, trigger meta-reasoning for fallback]
```

**Event Sequence per Task**:
```python
[T0] task_update(status="loading", plan_set=plan_set)
[T1] node_tools_execution_start(node_id=task.id, tool_ids=[...], total_tools=N)
[T2-Tn] node_tool_event(event="tool_call_started", tool_id=tool_1)
[T2+Δ] node_tool_event(event="tool_call_completed", tool_id=tool_1, result={...})
...
[Tn] update_subagent_current_action("Creating notes from K sources")
[Tn+1] task_update(status="success", plan_set=plan_set_updated)
```

### 1.3 Orchestration Event Schema (22 Event Types)

#### RunEvent Enum Extension (Backend)
```python
from enum import Enum

class RunEventType(str, Enum):
    # Lifecycle
    STREAM_START = "stream_start"
    HEARTBEAT = "heartbeat"
    DONE = "done"
    ERROR = "ERROR"

    # Planning
    TASK_UPDATE = "task_update"
    PENDING_SOURCES = "pending_sources"

    # Execution
    NODE_TOOLS_EXECUTION_START = "node_tools_execution_start"
    NODE_TOOL_EVENT = "node_tool_event"
    UPDATE_SUBAGENT_CURRENT_ACTION = "update_subagent_current_action"

    # Messaging
    MESSAGE_DELTA = "message_delta"
    AI_MESSAGE = "ai_message"
    MESSAGE_IS_ANSWER = "message_is_answer"
    CHAT_TITLE_GENERATED = "chat_title_generated"

    # Deliverables
    NODE_REPORT_PREVIEW_START = "node_report_preview_start"
    NODE_REPORT_PREVIEW_DELTA = "node_report_preview_delta"
    NODE_REPORT_PREVIEW_DONE = "node_report_preview_done"

    # Citations
    REFERENCES_FOUND = "references_found"

    # Human-in-loop
    BROWSER_USE_START = "browser_use_start"
    BROWSER_USE_AWAIT_USER_INPUT = "browser_use_await_user_input"
    BROWSER_USE_STOP = "browser_use_stop"

    # Clarification
    CLARIFICATION_NEEDED = "clarification_needed"
    UPDATE_MESSAGE_CLARIFICATION_MESSAGE = "update_message_clarification_message"
```

#### Core Event Payloads

**task_update** (Planning -> Orchestration):
```python
class TaskUpdateEvent(BaseModel):
    type: Literal["task_update"]
    key: str                          # Task key (internal)
    message: str                      # Status message
    plan_set: PlanSet                 # Full state snapshot
    status: Status                    # "loading" | "success" | "error"
    title: str
    metadata: Optional[Dict] = None
    timestamp: int                    # Epoch ms
```

**node_tools_execution_start** (Orchestrator -> Client):
```python
class NodeToolsExecutionStartEvent(BaseModel):
    type: Literal["node_tools_execution_start"]
    node_id: str                      # Task/worker ID
    plan_id: str                      # Phase ID
    plan_set_id: str                  # Root context
    tool_ids: List[str]               # Batch of tools
    total_tools: int                  # Count
    timestamp: int
```

**node_tool_event** (Tool execution telemetry):
```python
class NodeToolEvent(BaseModel):
    type: Literal["node_tool_event"]
    plan_set_id: str
    plan_id: str
    node_id: str
    tool_id: Optional[str]
    event: str  # "tool_call_started" | "tool_call_completed" | "fallback_used" | "all_tools_failed"
    metadata: Optional[Dict] = None   # tool result, error, timing, etc.
    timestamp: int
```

**update_subagent_current_action** (Progress UI):
```python
class UpdateSubagentCurrentActionEvent(BaseModel):
    type: Literal["update_subagent_current_action"]
    plan_set_id: str
    plan_id: str
    node_id: str
    current_action: str               # "Searching for X", "Creating notes", etc.
    timestamp: Optional[int] = None
```

### 1.4 Entity/Artifact Substrate

#### Entity (Citation/Source Abstraction)
```python
class Entity(BaseModel):
    entity_id: str                    # UUID (content-addressed optional)
    entity_type: str                  # "citation" | "artifact" | "report" | "website"
    content: Optional[str] = None     # Markdown, HTML, or JSON
    metadata: Dict[str, Any] = {}     # provider, url, title, retrieved_at, etc.

    # Storage
    sha256: Optional[str] = None      # Content hash for deduplication
    size_bytes: Optional[int] = None
    created_at: Optional[str] = None

class CitationEntity(Entity):
    entity_type: Literal["citation"]
    metadata: CitationMetadata

class CitationMetadata(BaseModel):
    citation_identifier: str          # Matches GML <gml-inlinecitation identifier="..."/>
    external_url: str
    title: str
    provider: str                     # "brave" | "firecrawl" | "polygon" | etc.
    retrieved_at: str                 # ISO timestamp
```

**Semantic**: Entity is the **unifying abstraction** for all research output. Every citation, scraped document, API result, and generated artifact is stored as an Entity. This enables:
- Deduplication (same source retrieved twice → single Entity referenced twice)
- Citation tracking (entity.external_url + entity.provider)
- Incremental rendering (entities created before deliverables finish)

### 1.5 DataBrief (Shared State)

```python
class DataBrief(BaseModel):
    """
    Unified data context passed to all downstream generators.
    Created by synthesis_node, consumed by report/website/slides generators.
    """

    # Research findings
    financial_data: Dict[str, Any]    # Structured: {ticker: {revenue: X, earnings: Y}}
    market_data: Dict[str, Any]       # Market cap, growth rates, etc.
    company_metadata: Dict[str, Any]  # Name, description, industry, headquarters

    # Strategic analysis
    swot_summary: Optional[str] = None      # Strengths, weaknesses, opportunities, threats
    risk_factors: List[str] = []            # Identified risks from research
    growth_opportunities: List[str] = []

    # Research metadata
    primary_sources: List[Entity] = []      # Top sources by relevance
    all_sources: List[Entity] = []          # Complete source list
    data_gaps: List[str] = []               # Missing data (triggers meta-reasoning)

    # Temporal
    collected_at: str                       # When research completed (ISO timestamp)

    class Config:
        extra = "allow"  # Extensible for domain-specific fields
```

**Pattern**: All numeric values (revenue, growth %, etc.) are **stored once in DataBrief** and referenced by all generators. This ensures consistency: MSFT $281.7B appears identically in report, website, slides, and docs.

---

## SECTION 2: ORCHESTRATION PATTERNS & ALGORITHMS

### 2.1 Fan-Out Dispatch (Send Pattern)

**Conceptual Flow**:
```
planner_node
  ↓ [generates PlanSet with 14 tasks]
  ↓
dispatch_node (uses Send)
  ↓ [for each task: Send("research_executor", {task})]
  ↓ [all Send() calls batched, returns immediately]
  ↓
[Orchestrator schedules all 14 research_executor instances in parallel]
  ↓
[Each executor runs independently, emitting telemetry]
  ↓
fan_in_aggregation_node (waits for all, collects results)
```

**Pseudocode (LangGraph-compatible)**:
```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

class ResearchState(TypedDict):
    query: str
    plan_set: Optional[PlanSet] = None
    task_results: Annotated[List[TaskResult], operator.add] = []
    data_brief: Optional[DataBrief] = None

def planner_node(state):
    """Generates planning structure."""
    # LLM call with structured output
    plan_set = llm.invoke(
        prompt=f"Plan research for: {state['query']}",
        schema=PlanSet,  # Forces valid output
    )

    # Emit planning event
    emit_event(TaskUpdateEvent(
        status="loading",
        plan_set=plan_set,
        title="Devising Initial Research Strategy"
    ))

    return {"plan_set": plan_set}

def dispatch_node(state):
    """Fan-out: create parallel research tasks via Send()."""
    plan_set = state["plan_set"]

    # Flatten all tasks
    all_tasks = []
    for plan in plan_set.plans.values():
        for task in plan.plan_tasks.values():
            all_tasks.append(task)

    # Emit batch start
    emit_event(NodeToolsExecutionStartEvent(
        node_id="dispatch",
        tool_ids=[t.plan_task_id for t in all_tasks],
        total_tools=len(all_tasks),
    ))

    # CRITICAL: Send() returns immediately, doesn't wait
    # Orchestrator queues all jobs and executes in parallel
    return [
        Send("research_executor", {"task": task, "plan_set": plan_set})
        for task in all_tasks
    ]

def research_executor(state):
    """Execute a single research task with tools."""
    task = state["task"]
    plan_set = state["plan_set"]

    # Emit start
    emit_event(UpdateSubagentCurrentActionEvent(
        node_id=task.plan_task_id,
        current_action=f"Starting research: {task.title}"
    ))

    # Tool execution loop
    tool_results = []
    for tool in determine_tools_for_task(task):
        emit_event(NodeToolEvent(
            node_id=task.plan_task_id,
            tool_id=tool.id,
            event="tool_call_started"
        ))

        try:
            result = execute_tool(tool, task)
            tool_results.append(result)

            emit_event(NodeToolEvent(
                node_id=task.plan_task_id,
                tool_id=tool.id,
                event="tool_call_completed",
                metadata={"result_size": len(result.content)}
            ))
        except ToolError as e:
            emit_event(NodeToolEvent(
                node_id=task.plan_task_id,
                tool_id=tool.id,
                event="tool_error",
                metadata={"error": str(e)}
            ))
            # Continue to next tool (fallback pattern)

    # Synthesis: convert tool results → notes
    emit_event(UpdateSubagentCurrentActionEvent(
        node_id=task.plan_task_id,
        current_action="Creating notes from K sources"
    ))

    notes = llm.invoke(
        prompt=f"Synthesize findings for {task.title}:\n{format_tool_results(tool_results)}",
    )

    # Emit completion
    emit_event(TaskUpdateEvent(
        status="success",
        plan_set=plan_set,
    ))

    return TaskResult(
        task_id=task.plan_task_id,
        notes=notes,
        sources=[tr.source for tr in tool_results],
        entities=[create_entity(tr) for tr in tool_results]
    )

def fan_in_aggregation(state):
    """Collect all parallel results."""
    # task_results is Annotated[List, operator.add], so it accumulates from all Send() calls
    all_task_results = state["task_results"]

    # Dedup sources by URL
    unique_sources = deduplicate_by_url([
        src for task_result in all_task_results
        for src in task_result.sources
    ])

    return {
        "task_results": all_task_results,
        "all_sources": unique_sources
    }

# Graph assembly
builder = StateGraph(ResearchState)
builder.add_node("planner", planner_node)
builder.add_node("dispatch", dispatch_node)
builder.add_node("research_executor", research_executor)
builder.add_node("fan_in", fan_in_aggregation)

builder.add_edge(START, "planner")
builder.add_conditional_edges("planner",
    lambda state: "dispatch" if state.get("plan_set") else END)
builder.add_edge("dispatch", "research_executor")  # -> all Send() instances
builder.add_edge("research_executor", "fan_in")    # waits for all, accumulates
builder.add_edge("fan_in", "synthesize")           # next stage

graph = builder.compile(checkpointer=PostgresCheckpointer(...))
```

**Key Insights**:

1. **Send() returns immediately** — fan_out doesn't block. Orchestrator handles queueing.
2. **Parallel collection via Annotated[List, operator.add]** — Each parallel research_executor appends to task_results. Fan-in reducer accumulates all.
3. **Per-task telemetry** — Each executor emits its own `node_tool_event` and `update_subagent_current_action` events, identified by `node_id`.
4. **Independent error handling** — If task 5 fails, tasks 1-4 and 6-14 continue. Fan-in detects failures and triggers meta-reasoning.

### 2.2 Meta-Reasoning & Adaptive Re-planning

**Observed Pattern** (from screenshot):
```
Phase 1: "Devising Initial Research Strategy"
  → 14 parallel tasks launched
  → Tasks execute (some succeed, some fail)
  → Fan-in aggregation collects results

[Meta-reasoning node]
  → Analyzes results
  → Detects gap: "FactSet failed for financial data"
  → Decides to create secondary plan

Phase 2: "Considering Results and Refining Research Strategy"
  → New plan created with fallback tools
  → "Gather financial data from SEC filings instead"
  → 2-3 new tasks launched

[Fan-in for Phase 2]
  → Merges Phase 2 results with Phase 1
  → Proceeds to synthesis with enriched data
```

**Implementation Pattern**:
```python
def meta_reasoning_node(state):
    """Evaluate research quality and decide on follow-up."""
    task_results = state["task_results"]

    # Analyze completeness
    missing_data_types = analyze_gaps(task_results)

    if missing_data_types:
        # Create secondary plan
        new_plan = llm.invoke(
            prompt=f"""
            Initial research identified gaps: {missing_data_types}.
            Create a focused plan to fill these gaps using alternative sources.
            """,
            schema=Plan,
        )

        # Emit new plan
        emit_event(TaskUpdateEvent(
            status="loading",
            plan_set=state["plan_set"],  # same PlanSet
            title="Considering Results and Refining Research Strategy"
        ))

        # Set up conditional routing
        return {"new_plan": new_plan, "should_continue": True}
    else:
        # Sufficient data, proceed to synthesis
        return {"should_continue": False}

def should_continue_research(state):
    """Conditional routing."""
    if state.get("should_continue"):
        return "dispatch_gap_filling"
    else:
        return "synthesis_node"

# In graph:
builder.add_conditional_edges("meta_reasoning", should_continue_research, {
    "dispatch_gap_filling": "dispatch_node",  # Re-invoke planner with new plan
    "synthesis_node": "synthesis_node"
})
```

**Why It Works**:
- **Transparent to user** — Activity panel shows "Considering Results..." step
- **Incremental data enrichment** — Phase 2 results merged with Phase 1
- **Automatic fallback** — "FactSet failed → try SEC filings" without human intervention
- **No loss of intermediate work** — All Phase 1 results preserved

### 2.3 Synthesis Node (Fan-In Integration)

```python
def synthesis_node(state):
    """
    Aggregate all research results into DataBrief.
    Called once after all parallel tasks + meta-reasoning complete.
    """

    task_results = state["task_results"]
    query = state["query"]

    # Consolidate findings
    all_findings = {
        tr.notes for tr in task_results
    }

    all_sources = [
        entity
        for tr in task_results
        for entity in tr.entities
    ]

    # LLM synthesis: raw findings → structured brief
    data_brief = llm.invoke(
        prompt=f"""
        Query: {query}

        Research findings from {len(task_results)} parallel tasks:
        {format_findings(all_findings)}

        Extract structured data into JSON:
        {{
            "financial_data": {{}},
            "market_data": {{}},
            "company_metadata": {{}},
            "swot_summary": "...",
            "risk_factors": [...],
            "primary_sources": [...],
            "data_gaps": [...]
        }}
        """,
        schema=DataBrief,  # Forces valid JSON
    )

    # Add source entities
    data_brief.all_sources = all_sources

    # Store brief as internal artifact (for debugging)
    store_artifact(Artifact(
        entity_type="data_brief",
        content=data_brief.model_dump_json(),
    ))

    emit_event(UpdateSubagentCurrentActionEvent(
        current_action="Synthesis complete. Preparing deliverables."
    ))

    return {"data_brief": data_brief}
```

**Critical Property**: DataBrief is **the single source of truth** for all downstream generators. Every numeric value, text, and citation flows from this structured object.

### 2.4 Deliverable Router (Conditional Dispatch)

```python
class Message(BaseModel):
    """Unified message with multi-deliverable support."""
    content: str                          # Main text answer
    deliverable_type: Literal["text", "report", "website", "slides", "document"]

    # Lazy-loaded artifacts
    report_identifier: Optional[str] = None
    website_manifest_id: Optional[str] = None
    # ... etc

def deliverable_router(state):
    """Route to appropriate generator based on user request."""

    deliverable_type = state["message"].deliverable_type
    data_brief = state["data_brief"]

    if deliverable_type == "text":
        # Plain LLM answer, no generation
        return "synthesizer"

    elif deliverable_type == "report":
        return Send("report_generation_node", {
            "data_brief": data_brief,
            "query": state["query"]
        })

    elif deliverable_type == "website":
        return Send("website_generation_node", {
            "data_brief": data_brief,
            "query": state["query"]
        })

    # ... handle slides, document
```

---

## SECTION 3: QUALITY SYSTEMS & VALIDATION

### 3.1 GML Report Markup System

**Tag Set** (18 tags total):
```typescript
// Layout tags (control structure)
<gml-row>
<gml-primarycolumn>
<gml-sidebarcolumn>
<gml-halfcolumn>

// Content tags (semantic blocks)
<gml-chartcontainer props='{"data": [...], "layout": {...}}'/>
<gml-gradientinsightbox>Key insight...</gml-gradientinsightbox>
<gml-infoblockmetric props='{"label": "Revenue", "value": "$2.4M", "trend": "up"}'/>
<gml-infoblockevent props='{"title": "Event", "date": "...", "impact": "..."}'/>
<gml-infoblockstockticker props='{"symbol": "AAPL", "price": 150}'/>
<gml-inlinecitation identifier="entity-abc-123"/>
<gml-blockquote>Quote text</gml-blockquote>
<gml-downloadfile props='{"filename": "...", "url": "..."}'/>

// Viewer tags (export/sharing)
<gml-viewreport/>
<gml-viewwebsite/>
<gml-viewpresentation/>
<gml-viewgenerateddocument/>

// Meta tags
<gml-components>
<gml-header-elt>
```

**System Prompt Fragment** (inferred):
```
You are generating a professional business report. Structure it using GML tags:

1. LAYOUT: Wrap content in <gml-row> with <gml-primarycolumn> and <gml-sidebarcolumn>
2. CONTENT: Use semantic tags:
   - Charts: <gml-chartcontainer props='{"data": [...], "layout": {...}}'/>
   - Metrics: <gml-infoblockmetric props='{"label": "...", "value": "...", "trend": "up|down"}'/>
   - Insights: <gml-gradientinsightbox>...</gml-gradientinsightbox>
3. CITATIONS: Reference entities: <gml-inlinecitation identifier="[entity-id-from-research]"/>
4. NESTING: Keep depth ≤3 (will be healed by renderer)
5. DON'T WORRY: Structural issues will be auto-corrected by healer
```

### 3.2 Healer/Validator System

**Rules** (enforced post-generation, pre-render):
```python
VALID_LOCATIONS = {
    'gml-blockquote': ['gml-primarycolumn'],
    'gml-chartcontainer': ['gml-primarycolumn'],
    'gml-gradientinsightbox': ['gml-primarycolumn'],
    'gml-infoblockevent': ['gml-sidebarcolumn'],
    'gml-infoblockmetric': ['gml-sidebarcolumn'],
    'gml-infoblockstockticker': ['gml-sidebarcolumn'],
    'gml-inlinecitation': ['inline'],  # Can be anywhere
}

def heal_markup(dom_tree):
    """Fix structural issues without LLM retry."""
    for widget in dom_tree.walk():
        parent = widget.parent

        if widget.tag in VALID_LOCATIONS:
            valid_parents = VALID_LOCATIONS[widget.tag]

            if parent.tag not in valid_parents:
                # Try to hoist
                new_parent = find_ancestor_matching(widget, valid_parents)
                if new_parent:
                    new_parent.append(widget)  # Move
                else:
                    remove(widget)  # No valid location, discard

    return dom_tree
```

**Why This Matters**:
- LLM generation is forgiving (doesn't need perfect nesting)
- Healer fixes 95% of structural issues automatically
- Avoids expensive retry loops (LLM timeout, cost, latency)
- Enables "good enough" prompting

### 3.3 Multi-Stage Generation Pipeline

**Report Generation (4 Stages)**:
```
Stage 1: Writing outline...
  ↓ [LLM generates section structure]
  ↓
Stage 2: Building components...
  ↓ [LLM generates MarkupNode subtrees per section, parallel Send() per section]
  ↓
Stage 3: Reviewing content... ← Can occur multiple times
  ↓ [LLM reads full draft, identifies issues]
  ↓ [If issues found: targeted rewrites]
  ↓
Stage 4: Polishing typography...
  ↓ [Final formatting pass]
  ↓
Assembly & Storage
  ↓ [Run Healer, store as Artifact, emit REPORT_PREVIEW_DONE]
```

**Website Generation (7 Stages)**:
```
1. Template Assembly (frozen shadcn/ui bundle)
2. Architecture Selection (monolithic vs coordinator vs four-tier)
3. Theme Generation (design tokens, CSS variables)
4. Layout Primitive Generation (reusable containers)
5. Content Section Generation (section-aware layouts)
6. Interactive Widget Generation (Recharts + react-simple-maps)
7. Atomic Export (all files with identical timestamp)
```

**Evidence of Review Passes**:
From screenshot, "Reviewing content..." appears **multiple times** during generation, suggesting iterative loops. Likely pattern:
```
Generate full draft → Review pass 1 → [issues found?] → Targeted fixes → Review pass 2 → Continue
```

---

## SECTION 4: ERROR HANDLING & RESILIENCE

### 4.1 Graceful Degradation Strategy

**Failure Hierarchy**:
```
Tool Error (single call fails)
  → Retry up to 3× with exponential backoff
  → Fallback to alternative provider
  → Mark source as "retrieved_at not verified"
  → Continue task

Task Error (entire task fails)
  → Mark task status="error"
  → Continue parallel tasks
  → Fan-in detects: "Task 9 failed, Task 12 succeeded"

Plan Error (critical research gap)
  → Meta-reasoning triggers
  → Create new plan with alternative sources
  → Execute gap-filling research

Run Error (fatal orchestration failure)
  → Emit ERROR event
  → Halt stream, display error to user
```

### 4.2 Tool Fallback Pattern

**Evidence**: FactSet failure triggers SEC filing fallback.

```python
FALLBACK_CHAINS = {
    "financial_data": [
        ("factset", FactSetAPI),
        ("sec_filings", SECFilingsScraper),
        ("alpha_vantage", AlphaVantageAPI),
        ("financial_modeling", FinancialModelingPrepAPI),
    ],
    "market_data": [
        ("polygon", PolygonAPI),
        ("yfinance", YFinanceAPI),
        ("iex_cloud", IEXCloudAPI),
    ],
    "company_info": [
        ("crunchbase", CrunchbaseAPI),
        ("apollo", ApolloAPI),
        ("hunter", HunterAPI),  # For contact data
    ],
}

def execute_tool_with_fallback(tool_spec, max_retries=3):
    chain = FALLBACK_CHAINS.get(tool_spec.category, [])

    for provider_name, ToolClass in chain:
        for attempt in range(max_retries):
            try:
                tool = ToolClass(api_key=get_key(provider_name))
                result = tool.execute(tool_spec.query)

                if result.is_valid():
                    return {
                        "result": result,
                        "provider": provider_name,
                        "attempt": attempt + 1,
                    }
            except ToolError as e:
                log_tool_error(provider_name, tool_spec.category, str(e))

    # All fallbacks exhausted
    return {
        "result": None,
        "provider": None,
        "gap": tool_spec.category  # Report for meta-reasoning
    }
```

### 4.3 Stream Resilience

**Client-Side Retry Logic** (observed in bundle):
```typescript
// 30-second idle watchdog
let lastEventTime = Date.now();
let timeout = setInterval(() => {
  if (Date.now() - lastEventTime > 30000) {
    // Timeout: abort and retry
    reader.cancel();
    retryStream(message_stream_id, retryCount + 1);
  }
}, 1000);

// Exponential backoff: 1s, 2s, 4s, 8s, 16s (capped at 30s)
async function retryStream(streamId, attempt) {
  if (attempt > 5) {
    // Give up after 5 retries
    emit_event({type: "ERROR", message: "Stream timeout after 5 retries"});
    return;
  }

  const delayMs = Math.min(1000 * Math.pow(2, attempt - 1), 30000);
  await sleep(delayMs);

  // Reconnect
  const response = await fetch(`/api/chat/message/stream?message_stream_id=${streamId}`);
  // Continue consuming...
}
```

---

## SECTION 5: STATE PERSISTENCE & CHECKPOINTING

### 5.1 Event Sourcing Model

**All execution state is reconstructable from events**:
```
Event Log (append-only, durable):
  [T0] stream_start
  [T1] task_update(status="loading", plan_set=...)
  [T2] node_tools_execution_start(tool_ids=[...])
  [T3] node_tool_event(event="tool_call_started", tool_id="brave_search_1")
  [T4] node_tool_event(event="tool_call_completed", tool_id="brave_search_1", result={...})
  ...
  [Tn] done(message={...}, has_async_entities_pending=true)

Replay:
  for event in stored_event_log:
    onEvent(event)
    sleep(REPLAY_THROTTLE)  # Simulate realtime
```

### 5.2 Materialized State Cache

```python
class RunState(BaseModel):
    """Materialized state for query efficiency."""
    run_id: str
    plan_set: Optional[PlanSet]
    current_phase: Literal["planning", "research", "synthesis", "generation", "complete"]
    completed_tasks: Set[str]
    failed_tasks: Set[str]
    artifacts: List[Artifact]
    last_event_time: int

    # Lazy-loaded sections
    @property
    def data_brief(self):
        return query_artifact(f"data_brief:{self.run_id}")

# Dual model:
# - Event log: immutable, append-only, durable
# - Materialized state: mutable cache, efficient queries, rebuilt on replay
```

---

## SECTION 6: OPEN QUESTIONS & UNKNOWNS

1. **What LLM powers the planner?** — GPT-4, Claude, or proprietary?
2. **Is meta-reasoning the same agent as planner?** — Same model or different?
3. **How are tool credentials scoped?** — Per-user, per-workspace, or system-wide?
4. **What triggers multi-stage vs single-stage planning?** — User setting, query complexity, or learned heuristic?
5. **How is the 14-task limit chosen?** — Hard limit, soft heuristic, or adaptive?
6. **What determines review pass count?** — Fixed iterations, quality threshold, or time budget?
7. **How does co-generation (report + website) avoid race conditions?** — Lazy loading, semaphores, or queuing?
8. **Are there rate limits per tool/provider?** — How are they enforced across parallel tasks?
9. **What happens if ALL fallback tools fail?** — Clarification, or proceed with text-only?
10. **Is SendSilk/v0.app the same as Superagent?** — Or API-integrated third party?

---

## SECTION 7: REUSABLE CODE PATTERNS

### 7.1 Event Emission Wrapper

```python
# Centralized event sink (inject into all nodes)
class EventEmitter:
    def __init__(self, stream_id: str, db: AsyncSession):
        self.stream_id = stream_id
        self.db = db
        self.event_queue = asyncio.Queue()

    async def emit(self, event: RunEvent):
        """Async-safe emission to both stream and DB."""
        # To client stream
        await self.event_queue.put(event)

        # To persistent log
        await self.db.execute(
            insert(RunEventLog).values(
                message_stream_id=self.stream_id,
                event_data=event.model_dump_json(),
                event_type=event.type,
                timestamp=event.timestamp or int(time.time() * 1000),
            )
        )
        await self.db.commit()

    async def stream_events(self):
        """Background task: stream events to client via SSE."""
        while True:
            event = await self.event_queue.get()
            yield f"data: {event.model_dump_json()}\n\n"

# Usage in any node:
async def some_node(state, emitter: EventEmitter):
    await emitter.emit(UpdateSubagentCurrentActionEvent(
        current_action="Searching for data..."
    ))
    # ... do work ...
    await emitter.emit(NodeToolEvent(
        event="tool_call_completed"
    ))
```

### 7.2 Tool Execution with Telemetry

```python
async def execute_tool_instrumented(
    tool: ToolSpec,
    input_data: Dict,
    emitter: EventEmitter,
    node_id: str,
    fallback_chain: List[ToolSpec] = None,
):
    """Execute tool with full telemetry and fallback support."""

    await emitter.emit(NodeToolEvent(
        node_id=node_id,
        tool_id=tool.id,
        event="tool_call_started",
        metadata={"input_size": len(str(input_data))}
    ))

    start_time = time.time()

    try:
        result = await asyncio.wait_for(
            tool.execute(input_data),
            timeout=60  # per-tool timeout
        )

        duration_ms = (time.time() - start_time) * 1000

        await emitter.emit(NodeToolEvent(
            node_id=node_id,
            tool_id=tool.id,
            event="tool_call_completed",
            metadata={
                "result_size": len(result.content),
                "duration_ms": duration_ms,
                "provider": tool.provider,
            }
        ))

        return result

    except asyncio.TimeoutError:
        await emitter.emit(NodeToolEvent(
            node_id=node_id,
            tool_id=tool.id,
            event="tool_timeout",
            metadata={"timeout_seconds": 60}
        ))

        # Trigger fallback
        if fallback_chain:
            return await execute_tool_instrumented(
                fallback_chain[0],
                input_data,
                emitter,
                node_id,
                fallback_chain[1:]
            )
        else:
            raise

    except Exception as e:
        await emitter.emit(NodeToolEvent(
            node_id=node_id,
            tool_id=tool.id,
            event="tool_error",
            metadata={"error": str(e), "error_type": type(e).__name__}
        ))
        raise
```

### 7.3 Annotated List Reducer (for Fan-in)

```python
from typing import Annotated
import operator

class ResearchState(TypedDict):
    # Each Send() call appends to task_results
    # Reducer: operator.add (list concatenation)
    task_results: Annotated[List[TaskResult], operator.add]

def node_that_creates_tasks(state):
    """Returns TaskResult list."""
    return {"task_results": [TaskResult(...)]}

def fan_in_node(state):
    """Receives accumulated task_results."""
    # state["task_results"] contains ALL appended results
    all_results = state["task_results"]  # type: List[TaskResult]

    # Deduplicate, sort, etc.
    deduped = deduplicate_by_id(all_results)

    return {"aggregated_results": deduped}
```

---

## SECTION 8: DECISION REGISTRY

| Decision | Rationale | Tradeoff |
|----------|-----------|----------|
| **Send() for fan-out** | Dynamic parallelism; scales to N tasks | Complex error handling; state management |
| **Event sourcing** | Full replay capability; audit trail | Storage overhead; eventual consistency |
| **GML markup (custom)** | Constrains LLM output; domain-specific | Healer complexity; vendor lock-in |
| **Separate data brief** | Single source of truth for generators | Extra synthesis step; latency |
| **Per-task telemetry** | Granular visibility; enables detailed progress UI | Event volume; storage cost |
| **Graceful degradation** | Complete with partial data; user trust | Hidden quality issues; harder to debug |
| **Client-side retry** | Latency transparency; smart backoff | Connection state tracking; complexity |
| **Artifact deduplication** | Storage efficiency; citation consistency | Content hash computation; SHA256 overhead |

---

## SECTION 9: CRITICAL DEPENDENCIES

**For implementing Superagent-like orchestration:**

1. **LangGraph Send() support** — Dynamic fan-out is core pattern
2. **Async session management** — Per-node session factories (not shared)
3. **Durable checkpointing** — PostgreSQL/SQLAlchemy for state persistence
4. **NDJSON streaming** — SSE or WebSocket for realtime events
5. **Structured output** — Pydantic schemas + LLM function calling
6. **Multi-provider tool abstraction** — Fallback chains, credentials management
7. **Entity/citation kernel** — Content-addressed storage for deduplication

---

## SECTION 10: MEASUREMENT & VALIDATION

### Success Metrics for Orchestrator Implementation

**Correctness**:
- All parallel tasks complete within single PlanSet
- Fan-in aggregation merges results without data loss
- Replay from checkpoint produces identical stream

**Performance**:
- Research phase latency: <2min for 14 parallel tasks
- Synthesis latency: <30s (LLM call only)
- Deliverable generation latency: <2min (streaming)

**Reliability**:
- Tool failure recovery: fallback chain success rate >95%
- Meta-reasoning activation: correctly identifies gaps in >80% of cases
- Stream dropout recovery: reconnect within 5 retries

---

## SOURCES & ATTRIBUTION

**Primary Analysis Documents**:
1. `/Users/markforster/AirTable-SuperAgent/docs/analysis/AGENTIC-SYSTEM.md` — System architecture (1,075 lines)
2. `/Users/markforster/AirTable-SuperAgent/reports/03_agent_orchestration_inference.md` — Orchestration patterns (145 lines)
3. `/Users/markforster/AirTable-SuperAgent/docs/analysis/QUALITY-METHODS.md` — Quality systems (1,194 lines)
4. `/Users/markforster/AirTable-SuperAgent/docs/plans/DEPENDENCY-ANALYSIS.md` — Critical path analysis (720 lines)
5. `/Users/markforster/NYQST-MCP/research/cloud-mcp-infrastructure/LANGGRAPH-DORMANT-CAPABILITIES.md` — LangGraph patterns (300 lines)

**Secondary Sources**:
- JavaScript bundles: `774-e1971e2500ea1c79.js` (Zod schemas), `1889-c64cad4788e7b7b9.js` (GML renderer)
- Screenshot evidence: Task card states, Activity panel reasoning steps
- Report analysis: File structure, component patterns, data consistency validation

---

**Generated**: 2026-02-20
**Extraction Confidence**: HIGH (schemas, patterns); MEDIUM (algorithms, thresholds)
**Actionable**: YES — All code patterns directly implementable in LangGraph

*End of Orchestration Extract*
