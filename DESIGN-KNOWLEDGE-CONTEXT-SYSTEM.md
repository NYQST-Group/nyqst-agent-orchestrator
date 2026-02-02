# Design Document: Knowledge, Context & Organisational Intelligence System

**Date:** 2026-02-01
**Author:** Mark Forster + Claude Opus 4.5
**Status:** DRAFT — for review and refinement
**Inputs:** PRD 02-06, ADR-001/005/006/008/009, Dify analysis (15 reports), PLATFORM_FOUNDATION.md

---

## 1. Problem Statement

NYQST's architectural foundations (substrate, run ledger, MCP tools) are strong but isolated. There is no system that:

1. **Persists conversations** — chat history disappears when the browser tab closes
2. **Binds agent context flexibly** — to any level of the organisational hierarchy (tenant, project, workflow, task, ad-hoc)
3. **Tags and classifies knowledge assets** — documents, conversations, insights, tools, environments
4. **Captures and reuses organisational learning** — lessons, methods, patterns from past work
5. **Enables cross-cutting queries** — "what did we learn across all logistics refinancings?"
6. **Unifies the tool registry** — MCP tools, platform tools, external services under one discovery and governance model
7. **Manages environments** — dev/staging/prod with appropriate tool and model bindings

The PRDs describe all of these capabilities across Modules 1-6, but no single design connects them into a buildable system with clear data models and phased delivery.

---

## 2. Design Principles

### From the PRDs (non-negotiable)

1. **Sovereignty** — All knowledge assets are owned by the tenant, stored in the substrate, never leaked across tenants
2. **Provenance** — Every insight traces back to its source conversation, message, run event, and artifacts
3. **Determinism** — Config resolution is reproducible: given the same hierarchy state, the same config is produced
4. **Audit** — The run ledger remains the authoritative record of what happened; this system adds the "why" and "what was learned"
5. **Agent-Assisted Mapping** — Agents propose, humans verify, trust builds incrementally

### From practical experience (this session)

6. **Flexible binding** — Don't hardcode hierarchy levels; use polymorphic scoping
7. **Snapshot at creation** — Resolve and freeze config when a conversation/run starts; don't re-resolve later
8. **Additive schema** — Each phase adds tables, never reworks existing ones
9. **Inherit and override** — Lower scopes inherit from higher, can override any field

---

## 3. The Hierarchy Model

### 3.1 Scope Hierarchy

```
Tenant (organisation)
  └── Environment (dev | staging | prod | client-sandbox)
        └── Project (e.g. "Battersea Refinancing Q1 2026")
              └── Objective (e.g. "Covenant compliance check")
                    └── Workflow (e.g. "Extract → Calculate → Report")
                          └── Task (e.g. "Extract DSCR from Q3 financials")
                                └── Conversation / Agent Run
```

Each level is optional. A conversation can be bound at ANY level:
- Tenant-level: ad-hoc exploration ("just ask a question")
- Project-level: "work on this project's documents"
- Task-level: "do this specific thing within this workflow"

### 3.2 Polymorphic Scope Binding

Rather than separate FKs for each level (which breaks when new levels are added):

```
scope_type  TEXT     — 'tenant' | 'environment' | 'project' | 'objective' | 'workflow' | 'task'
scope_id    UUID     — nullable (NULL for tenant-level)
```

Any entity that needs scoping uses this pair. Conversations, insights, tool registrations, knowledge assets.

### 3.3 Context Resolution

When a conversation or run starts, the system walks UP the hierarchy and merges configs:

```
1. Start at the bound scope (e.g. task)
2. Walk to parent (workflow → objective → project → environment → tenant)
3. At each level, merge:
   - mounted_pointers: UNION (additive)
   - allowed_tools: INTERSECT (restrictive — lower scopes can only narrow)
   - model_profile: OVERRIDE (most specific wins)
   - system_prompt_fragments: APPEND (each level adds context)
   - retrieval_config: OVERRIDE (most specific wins)
   - policy_template: OVERRIDE (most specific wins, must be >= parent strictness)
   - relevant_insights: RETRIEVE by tag + embedding similarity
4. Snapshot the resolved config as JSONB on the conversation/run
5. Record the inheritance chain for audit
```

**Merge semantics per field type:**

| Field | Merge Rule | Rationale |
|-------|-----------|-----------|
| mounted_pointers | Union | More context is usually better; tasks may add docs |
| excluded_pointers | Union | Exclusions accumulate (security) |
| allowed_tools | Intersect | Can only narrow, never widen (security) |
| blocked_tools | Union | Blocks accumulate |
| model_profile | Override (most specific) | Tasks may need different models |
| system_prompt | Append fragments | Each level adds relevant context |
| retrieval_config | Override (most specific) | Tasks may need different strategies |
| policy_template | Override (>= parent strictness) | Cannot relax governance |
| tags | Union | Tags accumulate down the hierarchy |

---

## 4. Data Models

### 4.1 Conversations & Messages (Priority 1)

```sql
-- Conversations: the container for a chat interaction
CREATE TABLE conversations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    user_id             UUID NOT NULL REFERENCES users(id),

    -- Polymorphic scope binding
    scope_type          TEXT NOT NULL DEFAULT 'tenant',
    scope_id            UUID,

    -- Module context (from ADR-006)
    module              TEXT,  -- 'research' | 'analysis' | 'document' | 'modelling' | 'knowledge' | 'insight'

    -- Resolved config snapshot (frozen at creation)
    config_snapshot     JSONB NOT NULL DEFAULT '{}',
    -- Contains: model, system_prompt, mounted_pointers, retrieval_config,
    --           allowed_tools, policy_template, inherited_from[]

    -- Metadata
    title               TEXT,  -- auto-generated or user-set
    status              TEXT NOT NULL DEFAULT 'active',  -- active | archived | deleted
    message_count       INTEGER NOT NULL DEFAULT 0,
    total_input_tokens  INTEGER NOT NULL DEFAULT 0,
    total_output_tokens INTEGER NOT NULL DEFAULT 0,
    total_cost_micros   BIGINT NOT NULL DEFAULT 0,  -- cost in microdollars for precision

    -- Agent binding
    agent_definition_id TEXT,
    langgraph_thread_id TEXT,

    -- Run ledger link
    run_id              UUID REFERENCES runs(id),

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_message_at     TIMESTAMPTZ,

    -- Indexes
    CONSTRAINT conversations_scope_check
        CHECK (scope_type IN ('tenant','environment','project','objective','workflow','task'))
);

CREATE INDEX idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX idx_conversations_scope ON conversations(scope_type, scope_id);
CREATE INDEX idx_conversations_user ON conversations(tenant_id, user_id);
CREATE INDEX idx_conversations_run ON conversations(run_id);


-- Messages: individual exchanges within a conversation
CREATE TABLE messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Content
    role                TEXT NOT NULL,  -- 'user' | 'assistant' | 'system' | 'tool'
    content             TEXT,           -- plain text content
    parts               JSONB,         -- AI SDK message parts (reasoning, tool_calls, sources, files)

    -- Metrics (from AI SDK result.usage)
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    cost_micros         BIGINT,         -- microdollars
    latency_ms          INTEGER,
    model_id            TEXT,           -- which model answered this message

    -- Status
    status              TEXT NOT NULL DEFAULT 'completed',  -- completed | error | cancelled | streaming
    error               JSONB,          -- error details if status = error

    -- Provenance links
    run_event_id        UUID,           -- links to specific run ledger event
    parent_message_id   UUID REFERENCES messages(id),  -- for conversation branching

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Ordering
    sequence_number     INTEGER NOT NULL
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence_number);
CREATE INDEX idx_messages_run_event ON messages(run_event_id);
CREATE INDEX idx_messages_parent ON messages(parent_message_id);


-- Message feedback: like/dislike + optional content
CREATE TABLE message_feedback (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id          UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id),
    rating              TEXT NOT NULL,  -- 'positive' | 'negative'
    content             TEXT,           -- optional explanation
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(message_id, user_id)
);
```

### 4.2 Universal Tagging System (Priority 1 — build alongside conversations)

```sql
-- Tags: universal classification for any entity
CREATE TABLE tags (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),

    -- What is tagged
    entity_type         TEXT NOT NULL,  -- 'artifact' | 'pointer' | 'conversation' | 'insight' |
                                        -- 'tool' | 'project' | 'workflow' | 'task' | 'agent_definition'
    entity_id           UUID NOT NULL,

    -- The tag itself
    namespace           TEXT NOT NULL,  -- 'domain' | 'asset_class' | 'task_type' | 'status' |
                                        -- 'skill' | 'method' | 'custom'
    key                 TEXT NOT NULL,  -- e.g. 'asset_class', 'sector', 'jurisdiction'
    value               TEXT NOT NULL,  -- e.g. 'logistics', 'uk', 'dscr_extraction'

    -- Provenance
    source              TEXT NOT NULL DEFAULT 'manual',  -- 'manual' | 'agent_proposed' | 'system' | 'inherited'
    confidence          FLOAT,          -- NULL for manual, 0-1 for agent-proposed
    verified_by         UUID REFERENCES users(id),
    verified_at         TIMESTAMPTZ,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Prevent duplicate tags
    UNIQUE(tenant_id, entity_type, entity_id, namespace, key, value)
);

CREATE INDEX idx_tags_entity ON tags(entity_type, entity_id);
CREATE INDEX idx_tags_lookup ON tags(tenant_id, namespace, key, value);
CREATE INDEX idx_tags_unverified ON tags(tenant_id, source, verified_at) WHERE verified_at IS NULL;
```

### 4.3 Insights (Priority 2 — after conversations are working)

```sql
-- Insights: organisational learning captured from work
CREATE TABLE insights (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),

    -- Where it was learned
    scope_type          TEXT NOT NULL,
    scope_id            UUID,

    -- What it came from
    source_type         TEXT NOT NULL,  -- 'conversation' | 'message' | 'run_event' | 'manual' | 'agent_proposed'
    source_id           UUID,

    -- The insight itself
    insight_type        TEXT NOT NULL,  -- 'lesson' | 'method' | 'pattern' | 'warning' | 'metric' | 'heuristic'
    title               TEXT NOT NULL,
    content             TEXT NOT NULL,  -- summary/index text (full content lives in substrate)
    structured_data     JSONB,          -- optional structured representation

    -- Substrate link (D9: insights are artifacts)
    artifact_sha256     TEXT REFERENCES artifacts(sha256),  -- the immutable insight content

    -- Trust
    confidence          FLOAT NOT NULL DEFAULT 0.0,  -- 0 = unverified proposal, 1 = human-verified
    status              TEXT NOT NULL DEFAULT 'proposed',  -- proposed | verified | rejected | superseded
    verified_by         UUID REFERENCES users(id),
    verified_at         TIMESTAMPTZ,
    superseded_by       UUID REFERENCES insights(id),

    -- Dedup tracking (D15)
    discovered_count    INTEGER NOT NULL DEFAULT 1,  -- incremented on auto-merge
    merged_from         UUID[],         -- IDs of insights that were merged into this one

    -- For semantic retrieval
    embedding           VECTOR(1536),   -- for finding relevant insights at context resolution time

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_insights_tenant ON insights(tenant_id, status);
CREATE INDEX idx_insights_scope ON insights(scope_type, scope_id);
CREATE INDEX idx_insights_type ON insights(tenant_id, insight_type);
CREATE INDEX idx_insights_embedding ON insights USING ivfflat (embedding vector_cosine_ops);
```

### 4.4 Tool Registry (Priority 2 — unifies MCP and platform tools)

```sql
-- Tool definitions: unified registry for all tools
CREATE TABLE tool_definitions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID,           -- NULL = system-wide (platform tools)

    -- Identity
    namespace           TEXT NOT NULL,  -- domain from ADR-008: 'substrate' | 'run' | 'knowledge' | 'connector' | etc.
    name                TEXT NOT NULL,  -- full name: 'substrate.pointer.list'
    display_name        TEXT NOT NULL,
    description         TEXT NOT NULL,

    -- Type
    tool_type           TEXT NOT NULL,  -- 'mcp_native' | 'platform' | 'external_mcp' | 'api' | 'workflow'
    mcp_server_id       TEXT,           -- which MCP server provides this (for mcp_native and external_mcp)

    -- Schema
    input_schema        JSONB NOT NULL, -- JSON Schema for parameters
    output_schema       JSONB,          -- JSON Schema for return value

    -- Capabilities and requirements
    capabilities        TEXT[],         -- which agent capabilities grant access to this tool
    required_scopes     TEXT[],         -- API key scopes needed
    side_effects        TEXT[],         -- 'read' | 'write' | 'external' | 'destructive'

    -- Governance
    default_gate        TEXT DEFAULT 'auto',  -- 'auto' | 'review' | 'approve' — default policy gate
    audit_level         TEXT DEFAULT 'standard',  -- 'none' | 'standard' | 'detailed'

    -- Metadata
    version             TEXT NOT NULL DEFAULT '1.0.0',
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(tenant_id, name, version)
);

CREATE INDEX idx_tools_tenant ON tool_definitions(tenant_id, is_active);
CREATE INDEX idx_tools_namespace ON tool_definitions(namespace);
CREATE INDEX idx_tools_type ON tool_definitions(tool_type);
CREATE INDEX idx_tools_capabilities ON tool_definitions USING GIN (capabilities);
```

### 4.5 Sessions (Priority 1 — built alongside conversations)

A session is an **environment lifecycle**: a running context from start to finish. It contains conversations, runs, and workspace state. Future: backed by a VM with hard resource boundaries. Pre-VM: bounded by inactivity gates.

```sql
-- Sessions: environment lifecycle from start to finish
CREATE TABLE sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    user_id             UUID NOT NULL REFERENCES users(id),

    -- Polymorphic scope binding (what is this session working on?)
    scope_type          TEXT NOT NULL DEFAULT 'tenant',
    scope_id            UUID,

    -- Module context (from ADR-006)
    module              TEXT,  -- 'research' | 'analysis' | 'document' | 'modelling' | 'knowledge' | 'insight'
    objective           TEXT,  -- what the user is trying to accomplish

    -- Resolved config (frozen at session start, governs all conversations within)
    config_snapshot     JSONB NOT NULL DEFAULT '{}',

    -- Resource mounts (what this session can access)
    mounted_pointers    UUID[],
    mounted_kbs         UUID[],
    pinned_artifacts    TEXT[],  -- SHA-256 strings

    -- Agent binding
    agent_definition_id TEXT,

    -- Lifecycle
    status              TEXT NOT NULL DEFAULT 'active',
                        -- active: user is working
                        -- idle: inactivity gate triggered, can resume
                        -- paused: user explicitly paused
                        -- closed: session ended, outputs published to substrate
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_active_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    idle_timeout_minutes INTEGER NOT NULL DEFAULT 30,  -- pre-VM inactivity gate
    closed_at           TIMESTAMPTZ,
    close_reason        TEXT,  -- 'user_ended' | 'inactivity' | 'timeout' | 'error'

    -- Workspace state (UI layout — not authoritative, per ADR-006)
    workspace           JSONB,

    -- Cost tracking (sum of all conversations + infrastructure)
    total_cost_micros   BIGINT NOT NULL DEFAULT 0,

    -- Future: VM binding
    vm_id               TEXT,           -- nullable until VM-backed sessions
    vm_started_at       TIMESTAMPTZ,
    vm_stopped_at       TIMESTAMPTZ,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_sessions_tenant ON sessions(tenant_id, status);
CREATE INDEX idx_sessions_user ON sessions(tenant_id, user_id);
CREATE INDEX idx_sessions_scope ON sessions(scope_type, scope_id);
CREATE INDEX idx_sessions_active ON sessions(status, last_active_at) WHERE status = 'active';
```

Conversations gain a `session_id` FK:

```sql
ALTER TABLE conversations ADD COLUMN session_id UUID REFERENCES sessions(id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
```

The relationship: Session (1) → Conversations (many). A session's config_snapshot governs all conversations within it. Individual conversations can narrow (not widen) the session's config via their own scope binding.

### 4.6 Tag Registries & Schema Store (Priority 2 — enables governed tagging)

```sql
-- Tag registries: define allowed tag namespaces, keys, and values
CREATE TABLE tag_registries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID,           -- NULL = platform-level (core tags)

    -- Identity
    namespace           TEXT NOT NULL,  -- 'asset_class' | 'task_type' | 'jurisdiction' | custom
    description         TEXT NOT NULL,
    registry_type       TEXT NOT NULL,  -- 'core' | 'custom'

    -- Governance
    managed_by          TEXT NOT NULL DEFAULT 'system',  -- 'system' | 'tenant_admin' | 'any_user'
    validation_mode     TEXT NOT NULL DEFAULT 'registry',  -- 'registry' (must match allowed values) | 'open' (any value)

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(tenant_id, namespace)
);

-- Tag registry values: allowed values for a namespace
CREATE TABLE tag_registry_values (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registry_id         UUID NOT NULL REFERENCES tag_registries(id) ON DELETE CASCADE,

    value               TEXT NOT NULL,
    display_name        TEXT NOT NULL,
    description         TEXT,
    parent_value_id     UUID REFERENCES tag_registry_values(id),  -- for hierarchical taxonomies
    sort_order          INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT true,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(registry_id, value)
);

CREATE INDEX idx_tag_registry_values_registry ON tag_registry_values(registry_id, is_active);


-- Schema definitions: structured types for domain concepts
-- Backs the Analysis and Modelling modules, tag registries, ontology classes
CREATE TABLE schema_definitions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID,           -- NULL = platform-level

    -- Identity
    namespace           TEXT NOT NULL,  -- 'cre' | 'regulatory' | 'finance' | custom domain
    name                TEXT NOT NULL,  -- 'dscr_covenant' | 'lease' | 'property'
    version             TEXT NOT NULL DEFAULT '1.0.0',
    display_name        TEXT NOT NULL,
    description         TEXT,

    -- The schema itself
    schema_type         TEXT NOT NULL,  -- 'structured_type' | 'ontology_class' | 'relationship_type' | 'enum'
    definition          JSONB NOT NULL, -- JSON Schema for structured_type; class definition for ontology_class
    -- structured_type example:
    --   {"fields": {"ratio": {"type": "number"}, "test_frequency": {"type": "string", "enum": ["monthly","quarterly"]}}}
    -- ontology_class example:
    --   {"superclass": "financial_metric", "properties": {"measured_on": "date", "applies_to": "loan"}}
    -- relationship_type example:
    --   {"source_class": "covenant", "target_class": "loan", "cardinality": "many_to_one", "inverse": "has_covenants"}

    -- Governance
    status              TEXT NOT NULL DEFAULT 'draft',  -- 'draft' | 'active' | 'deprecated' | 'superseded'
    superseded_by       UUID REFERENCES schema_definitions(id),

    -- Substrate link (schemas are artifacts too)
    artifact_sha256     TEXT REFERENCES artifacts(sha256),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(tenant_id, namespace, name, version)
);

CREATE INDEX idx_schema_defs_tenant ON schema_definitions(tenant_id, status);
CREATE INDEX idx_schema_defs_type ON schema_definitions(schema_type, namespace);
```

The schema store is exposed via Platform MCP tool namespace `schema.*`:
- `schema.register` — create/update a schema definition
- `schema.validate` — validate data against a schema
- `schema.list` — list schemas by namespace/type
- `schema.get` — get schema definition with full JSON Schema

Tag Service MCP uses tool namespaces:
- `tag.core.set` — set a core tag (validates against registry, requires system auth)
- `tag.core.list_registries` — list core tag namespaces and allowed values
- `tag.custom.set` — set a custom tag (tenant auth, registry validation if registry exists)
- `tag.custom.create_registry` — create a custom tag namespace with allowed values

### 4.7 Environments (Priority 3)

```sql
-- Environments: dev/staging/prod with distinct configs
CREATE TABLE environments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    name                TEXT NOT NULL,  -- 'development' | 'staging' | 'production' | custom
    slug                TEXT NOT NULL,
    description         TEXT,

    -- Config overrides for this environment
    model_profile       JSONB,          -- model overrides (e.g. dev uses gpt-4o-mini)
    tool_overrides      JSONB,          -- tool availability/config per environment
    feature_flags       JSONB,          -- feature toggles per environment
    secrets_ref         TEXT,           -- reference to secrets store (not inline)

    is_default          BOOLEAN NOT NULL DEFAULT false,
    status              TEXT NOT NULL DEFAULT 'active',

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(tenant_id, slug)
);
```

### 4.6 Scope Config (Priority 3 — enables the inheritance chain)

```sql
-- Scope configs: configuration at any hierarchy level
CREATE TABLE scope_configs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),

    -- Which scope this config belongs to
    scope_type          TEXT NOT NULL,
    scope_id            UUID,

    -- Configuration fields (all nullable — unset means inherit from parent)
    mounted_pointers    UUID[],
    excluded_pointers   UUID[],
    allowed_tools       TEXT[],         -- tool names that are allowed
    blocked_tools       TEXT[],         -- tool names that are blocked
    model_profile       JSONB,
    system_prompt_fragment TEXT,        -- appended to parent's prompt
    retrieval_config    JSONB,          -- top_k, strategy, rerank, etc.
    policy_template     TEXT,           -- 'exploratory' | 'standard' | 'regulated' | 'audit_critical'

    -- Metadata
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(tenant_id, scope_type, scope_id)
);

CREATE INDEX idx_scope_configs_scope ON scope_configs(scope_type, scope_id);
```

---

## 5. How Cross-Org Intelligence Works

### 5.1 The Learning Loop

```
┌─────────────────────────────────────────────────────────┐
│  WORK                                                    │
│  Conversation → Messages → Run Events → Artifacts        │
│         │                                                │
│         ▼                                                │
│  CAPTURE                                                 │
│  Agent proposes insight (confidence: 0.0-0.7)           │
│  OR human creates insight manually (confidence: 1.0)     │
│         │                                                │
│         ▼                                                │
│  TAG                                                     │
│  Insight tagged: task_type=covenant_extraction,          │
│                  asset_class=logistics,                   │
│                  jurisdiction=uk                          │
│         │                                                │
│         ▼                                                │
│  VERIFY (agent-assisted mapping)                         │
│  Human reviews proposed insight → approve/reject/edit    │
│  Confidence updated, verified_by recorded                │
│         │                                                │
│         ▼                                                │
│  INJECT                                                  │
│  Next conversation with matching tags/scope:             │
│  Context resolution retrieves relevant insights          │
│  Injected into system prompt as organisational context   │
│         │                                                │
│         ▼                                                │
│  WORK (improved)                                         │
│  Agent operates with accumulated organisational knowledge│
└─────────────────────────────────────────────────────────┘
```

### 5.2 Cross-Project Queries

The universal tagging system enables:

**By tag:**
```sql
-- All conversations about logistics refinancings
SELECT c.* FROM conversations c
JOIN tags t ON t.entity_type = 'conversation' AND t.entity_id = c.id
WHERE t.tenant_id = :tenant
  AND t.key = 'asset_class' AND t.value = 'logistics'
  AND c.scope_type = 'project';
```

**By insight type:**
```sql
-- All verified lessons about covenant extraction
SELECT * FROM insights
WHERE tenant_id = :tenant
  AND insight_type = 'method'
  AND status = 'verified'
  AND id IN (
    SELECT entity_id FROM tags
    WHERE entity_type = 'insight'
      AND key = 'task_type' AND value = 'covenant_extraction'
  );
```

**By embedding similarity:**
```sql
-- Find insights relevant to a new query
SELECT *, embedding <=> :query_embedding AS distance
FROM insights
WHERE tenant_id = :tenant
  AND status = 'verified'
  AND confidence >= 0.7
ORDER BY distance
LIMIT 10;
```

**Coaching reports (from PRD 06_ARCHITECTURE §693-708):**
```sql
-- Cross-session analysis: find patterns in how users work
SELECT
    t.value AS task_type,
    COUNT(DISTINCT c.id) AS conversation_count,
    AVG(c.total_input_tokens + c.total_output_tokens) AS avg_tokens,
    AVG(c.message_count) AS avg_messages,
    COUNT(DISTINCT i.id) AS insights_generated
FROM conversations c
JOIN tags t ON t.entity_type = 'conversation' AND t.entity_id = c.id AND t.key = 'task_type'
LEFT JOIN insights i ON i.source_type = 'conversation' AND i.source_id = c.id
WHERE c.tenant_id = :tenant
GROUP BY t.value
ORDER BY conversation_count DESC;
```

### 5.3 Insight Injection at Context Resolution

When a new conversation starts:

```python
def resolve_context(scope_type: str, scope_id: UUID | None, tenant_id: UUID) -> ConfigSnapshot:
    # 1. Walk hierarchy, merge configs (as described in §3.3)
    config = merge_hierarchy_configs(scope_type, scope_id, tenant_id)

    # 2. Collect tags from the scope and its parents
    scope_tags = collect_tags_from_hierarchy(scope_type, scope_id, tenant_id)

    # 3. Retrieve relevant insights
    #    a. By tag match (exact)
    tag_matched = query_insights_by_tags(tenant_id, scope_tags, status='verified', min_confidence=0.7)

    #    b. By embedding similarity (semantic)
    if config.system_prompt:
        prompt_embedding = embed(config.system_prompt)
        semantic_matched = query_insights_by_embedding(tenant_id, prompt_embedding, limit=5)
    else:
        semantic_matched = []

    # 4. Deduplicate and rank
    relevant_insights = deduplicate_and_rank(tag_matched + semantic_matched, limit=10)

    # 5. Inject into system prompt
    if relevant_insights:
        config.system_prompt += "\n\n## Organisational Context\n"
        config.system_prompt += "The following lessons and methods are relevant to this work:\n"
        for insight in relevant_insights:
            config.system_prompt += f"- [{insight.insight_type}] {insight.content}\n"
            config.system_prompt += f"  (Source: {insight.source_type}, Confidence: {insight.confidence})\n"

    # 6. Record what was injected (for audit)
    config.injected_insights = [i.id for i in relevant_insights]
    config.inherited_from = build_inheritance_chain(scope_type, scope_id)

    return config
```

---

## 6. Tool Registry Design

### 6.1 Unified Tool Discovery

ADR-008 defines tool discovery as context-scoped. The tool registry extends this:

```python
def discover_tools(conversation: Conversation) -> list[ToolDefinition]:
    config = conversation.config_snapshot

    # 1. Get all active tools for this tenant + system tools
    all_tools = query_tools(tenant_id=conversation.tenant_id, is_active=True)
    all_tools += query_tools(tenant_id=None, is_active=True)  # system tools

    # 2. Filter by agent capabilities
    if config.get('agent_definition'):
        agent = get_agent_definition(config['agent_definition'])
        all_tools = [t for t in all_tools if set(t.capabilities) & set(agent.capabilities)]

    # 3. Filter by allowed/blocked tools from scope config
    if config.get('allowed_tools'):
        all_tools = [t for t in all_tools if matches_pattern(t.name, config['allowed_tools'])]
    if config.get('blocked_tools'):
        all_tools = [t for t in all_tools if not matches_pattern(t.name, config['blocked_tools'])]

    # 4. Filter by environment
    env = config.get('environment')
    if env and env.get('tool_overrides'):
        all_tools = apply_env_overrides(all_tools, env['tool_overrides'])

    # 5. Filter by policy (from ADR-009)
    policy = get_policy_template(config.get('policy_template', 'standard'))
    # Don't remove tools, but annotate which ones require approval
    for tool in all_tools:
        tool.requires_approval = check_gate(tool, policy)

    return all_tools
```

### 6.2 Tool Types

| Type | Example | Discovery | Execution |
|------|---------|-----------|-----------|
| `mcp_native` | `substrate.pointer.list` | Built-in, always available | Direct service call |
| `platform` | `document.classify` | Registered in tool_definitions | Internal function call |
| `external_mcp` | `browser.search` | Registered + MCP server config | MCP protocol call |
| `api` | `hubspot.update_deal` | Registered + connector config | HTTP call via connector |
| `workflow` | `covenant.compliance_check` | Registered when workflow published | Workflow execution engine |

All types share the same governance pipeline: Validate → Policy Check → Execute → Log → Return (ADR-008 §87-121).

---

## 7. Build Phases

### Phase 1: Conversations + Tags (Enables working chat product)

**New tables:** conversations, messages, message_feedback, tags
**Changes:** Wire AI SDK `onFinish` → `saveChat()`, load previous conversations
**Effort estimate concept:** Moderate — database + API + UI

**What it enables:**
- Persistent chat with history sidebar
- Resume conversations across sessions/devices
- Token counting and cost tracking per message
- Basic feedback (like/dislike)
- Tag conversations and artifacts by project, asset class, task type
- Link messages to run ledger events
- Agent-proposed tags on conversations (automatic classification)
- Query conversations by scope and tags

**Dify features this replaces:** Conversation model, message persistence, feedback, token/cost tracking

### Phase 2: Insights + Tool Registry (Enables organisational learning)

**New tables:** insights, tool_definitions
**Changes:** Insight creation from conversations, tool registry population, insight embedding
**Effort estimate concept:** Moderate-Large

**What it enables:**
- Agents propose insights from completed work
- Humans verify/reject/edit proposed insights
- Insights tagged and embedded for retrieval
- Unified tool registry (MCP + platform + external)
- Tool discovery respects scope, policy, and environment
- Cross-project queries by tag and embedding similarity
- Basic coaching reports (which task types generate most insights, token usage patterns)

**Dify features this replaces:** Annotation system (but ours is broader — not just message corrections, but organisational knowledge)

### Phase 3: Environments + Scope Configs (Enables config inheritance)

**New tables:** environments, scope_configs
**Changes:** Context resolution engine, config snapshot on conversation creation
**Effort estimate concept:** Moderate

**What it enables:**
- Full hierarchy-based config inheritance
- Environment-specific model and tool bindings
- System prompt composition from hierarchy fragments
- Policy escalation (child scopes cannot relax parent governance)
- Insight injection into context resolution
- Reproducible agent context (snapshot + inheritance chain for audit)

**This does NOT require projects/workflows/tasks to exist yet** — those entities can be added to the hierarchy later. The scope_configs table works with whatever scope_types are defined.

### Phase 4: Cross-Org Intelligence (The core differentiator)

**New tables:** None (uses insights + tags + conversations)
**Changes:** Analytics queries, coaching report generation, background insight aggregation
**Effort estimate concept:** Variable — depends on reporting depth

**What it enables:**
- "Coach these sessions" — pattern detection across conversations
- "User coaching report" — recurring patterns per user
- "Org-wide coaching report" — organisational learning summary
- Method libraries — verified insights grouped by task type
- Performance benchmarks — how long does covenant extraction take?
- Insight propagation — lessons from one project improve another
- Background copilot (from PRD 03_PLATFORM §427-437) — always-running agent that detects opportunities and builds institutional knowledge

**This is NOT "eventually"** — this is the product. PropSygnal's value is not "extract covenants" (anyone can do that). It's "extract covenants better every time because the system learns from every extraction." The cross-org intelligence is what makes it worth £200k/year.

---

## 8. Relationship to Existing ADRs

| ADR | Relationship to this Design |
|-----|---------------------------|
| **ADR-001** (Data Model) | This design extends the substrate with conversations, insights, and tags — all domain-first, not CDM |
| **ADR-005** (Agent Runtime) | Conversations link to LangGraph threads; config snapshots include agent definitions; run ledger is the authoritative audit, conversations are the user-facing view |
| **ADR-006** (Session Architecture) | Sessions can BE conversations or CONTAIN conversations. The scope binding model extends ADR-006's context inheritance beyond sessions to the full hierarchy. Session.module maps to conversation.module |
| **ADR-008** (MCP Tools) | Tool registry formalises what ADR-008 describes as "tool discovery." Adds persistence, versioning, environment binding, and unified governance for non-MCP tools |
| **ADR-009** (Governance) | Policy templates from ADR-009 are referenced in scope_configs and applied during tool discovery. Approval requests link to conversations and messages |

---

## 9. Relationship to Dify Analysis

| Dify Feature | Our Equivalent | Difference |
|-------------|---------------|-----------|
| Conversation + Messages | conversations + messages tables | Ours adds: polymorphic scope binding, config snapshot, run ledger link, cost in microdollars |
| Message Feedback | message_feedback table | Equivalent |
| Message Annotations (human overrides with embedding match) | insights table with source_type='message' | Ours is broader — not just "correct this answer" but "capture this as organisational knowledge" |
| App Configuration | scope_configs + config_snapshot | Ours is hierarchical and inheritable; Dify's is per-app flat config |
| 7 App Modes | conversation.module + scope config | We don't need 7 modes; the module field + scope config provides flexibility |
| Tool Provider Architecture | tool_definitions table | Ours unifies MCP + platform + external under one registry with governance |
| Analytics (on-the-fly GROUP BY) | Pre-computed via tags + insights | Ours is tag-based and embeddable, not just SQL aggregation |
| Workflow DSL | scope_type='workflow' + scope_configs | Ours is scope-based config, not a visual DSL (workflow engine is separate) |

---

## 10. What This Design Does NOT Cover

These are explicitly out of scope and will be separate designs:

1. **Workflow engine** — Visual DAG builder, node types, execution engine. This design provides the scope binding and config for workflows, not the workflow engine itself.
2. **Project/Objective/Task models** — The actual entities. This design provides the polymorphic scope binding that they plug into. The entities themselves need their own design (likely aligned with PropSygnal's domain model).
3. **Ontology management** — Domain models, entity definitions, relationship mapping. Module 5 from the PRDs. This design's tagging system is a lightweight precursor; full ontology management is a separate system.
4. **Background copilot** — The always-running agent from PRD §427-437. This design provides the data (insights, tags, cross-project queries) that the copilot would use. The copilot agent itself is separate.
5. **Document Classification Service** — ML-based taxonomy matching from PRD §391-399. This design's tags can receive classifications from that service.
6. **Connector framework** — External system integrations. The tool registry can register connector tools, but the connector framework (auth, sync, webhooks) is separate.

---

## 11. Open Questions

1. ~~Should insights have their own substrate representation?~~ **RESOLVED (D9):** Yes. Insights are substrate artifacts. The `insights` table is the metadata/index layer.

2. ~~Tag namespaces~~ **RESOLVED (D11):** Two-tier tag system. Core tags (system-managed, consistent namespaces like `asset_class`, `task_type`, `jurisdiction`) are written only by the Tag Service MCP with enforced registry validation. Custom tags (tenant-managed, any namespace) use the same MCP but with different auth scope. Both backed by per-tenant tag registries with descriptions and allowed values. The tag registries are part of a broader **schema/data model store** within Platform MCP (D12) that also serves the Analysis and Modelling modules.

3. **Insight embedding model** — Should insight embeddings use the same model as document embeddings, or a separate model optimised for short text? Different models = can't mix in the same vector queries. **Leaning:** same model for simplicity.

4. ~~Cross-tenant insights~~ **RESOLVED (D13):** Never share. Pure tenant isolation. Each tenant builds their own knowledge. NYQST (the company) can create platform-level domain model knowledge manually, but tenant insights never cross boundaries.

5. ~~Conversation branching~~ **RESOLVED (D10):** Yes, Phase 1. Schema already supports it via `parent_message_id`.

6. ~~Session vs Conversation~~ **RESOLVED (D8):** A session is an environment lifecycle (start → work → finish). Contains multiple conversations. Future: VM-backed with hard start/stop. Pre-VM: inactivity timeout gates.

7. ~~Session lifecycle gates~~ **RESOLVED (D14):** Auto-idle after 30 minutes inactivity (session moves to `idle`, resumable). Explicit "End Session" closes permanently. Both available. Auto-idle is a soft gate — user returns and the session resumes seamlessly.

8. ~~Insight deduplication~~ **RESOLVED (D15):** Auto-merge with count, BUT a duplicate insight triggers a diagnostic action. If an agent raises an insight that already exists (by embedding similarity), the system: (a) merges with incremented `discovered_count`, (b) logs a **context_injection_miss** event investigating why the original insight wasn't in the raising agent's context or wasn't understood by it. This is a signal of either a context resolution failure (insight wasn't retrieved) or an insight quality problem (insight was present but not actionable). If the fix is obvious (e.g. insight was below the similarity threshold, or the conversation's scope didn't match the insight's tags), the system auto-uplifts — adjusts tags, lowers threshold, or re-embeds. Non-obvious cases surface to a human reviewer.

9. ~~Session cost accounting~~ **RESOLVED (D16):** Track everything: LLM token costs, infrastructure (VM runtime when available, storage delta, external API calls), AND session duration as proxy for analyst hours displaced. Full unit economics from day one. This enables "this covenant compliance session cost £47 and took 12 minutes vs 4 hours manual" — the core business case.

---

## 12. Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| D1 | Polymorphic scope binding over separate FKs | Extensible without schema changes; new scope types just need new entity tables | 2026-02-01 |
| D2 | Config snapshot on conversation creation | Reproducibility; avoids re-resolution drift; audit-friendly | 2026-02-01 |
| D3 | Universal tagging over per-entity classification columns | One query model for all entities; enables cross-cutting analytics | 2026-02-01 |
| D4 | Insights as first-class entities with embeddings | Enables semantic retrieval for context injection; agent-assisted mapping pattern | 2026-02-01 |
| D5 | Cost in microdollars (BIGINT) over DECIMAL | Avoids floating-point precision issues; $1.00 = 1,000,000 microdollars | 2026-02-01 |
| D6 | Tool registry in DB over config files | Enables tenant-specific tools, versioning, governance, environment binding | 2026-02-01 |
| D7 | Cross-org intelligence as Phase 4, not "eventually" | This IS the product differentiator; defer beyond Phase 4 = defer the moat | 2026-02-01 |
| D8 | Session = environment lifecycle from start to finish | A session is a running environment (future: VM with hard start/stop; pre-VM: inactivity timeout gates). Not to be confused with LLM provider sessions. A session contains multiple conversations. | 2026-02-01 |
| D9 | Insights stored as substrate artifacts | Insights are written to the substrate (content-addressed, immutable) so they get the same provenance guarantees as documents. The `insights` table is the index/metadata layer; the insight content itself is an artifact. This means insights are referenceable by manifests, versionable, and auditable with zero extra infrastructure. | 2026-02-01 |
| D10 | Conversation branching supported from Phase 1 | `parent_message_id` FK on messages is used from day one. Edit-and-branch creates a new message with the same parent as the edited message's successor. UI: sibling navigation arrows (like Dify). This is cheap in the schema (already there) and high-value for exploratory research workflows where users want to try alternative prompts. | 2026-02-01 |
| D11 | Two-tier tag system: core (system-governed) + custom (tenant-governed) | Core tags have enforced registries (allowed namespaces, values, descriptions). Custom tags are freeform per tenant. Both accessed via Tag Service MCP with different auth scopes. Ensures cross-cutting query consistency for platform analytics while giving tenants flexibility. | 2026-02-01 |
| D12 | Schema/data model store as Platform MCP module | Tag registries, domain model schemas, ontology definitions, and structured type definitions share the same infrastructure within Platform MCP (namespace: `schema.*`, `tag.core.*`, `tag.custom.*`). Simpler deployment than separate MCP server. Supports both structured types (fields, validation) AND ontology relationships (class hierarchies, property constraints). | 2026-02-01 |
| D13 | Never share insights across tenants | Pure tenant isolation. NYQST can create platform-level domain model knowledge manually, but tenant-generated insights never cross boundaries. Sovereignty maximised. | 2026-02-01 |
| D14 | Auto-idle (30min) + manual end for sessions | Sessions auto-archive to `idle` after 30 minutes inactivity (resumable). Explicit "End Session" closes permanently. Soft gate — user returns and resumes seamlessly. | 2026-02-01 |
| D15 | Insight dedup = auto-merge + diagnostic action | Duplicate insight triggers `context_injection_miss` investigation: why wasn't the existing insight known to or used by the agent? Auto-uplift if fix is obvious (re-tag, re-embed, adjust threshold). Surface to human if not. A duplicate is a system health signal, not just a data quality issue. | 2026-02-01 |
| D16 | Track full unit economics: LLM + infra + time | Session cost = token costs + VM runtime + storage delta + external API calls + duration. Enables "this session cost £47 and took 12 minutes vs 4 hours manual." Core to the £200k/year business case. | 2026-02-01 |
