# Dify Tool & Plugin System: Architecture Analysis for Clean-Room Reimplementation

**Date:** 2026-02-01
**Scope:** Dify open-source codebase (upstream)
**Purpose:** Describe architecture patterns sufficient for independent reimplementation

---

## 1. Executive Summary

Dify's tool system is built around a **provider-tool two-level hierarchy** with a unified invocation pipeline. There are six tool provider types: built-in (hardcoded), plugin (daemon-managed), API (OpenAPI-imported), workflow-as-tool, MCP (Model Context Protocol), and dataset-retrieval. All share the same base abstractions (`Tool`, `ToolProviderController`, `ToolRuntime`) and produce the same output type (`ToolInvokeMessage`). Credentials are encrypted per-tenant, cached in a singleton pattern, and validated at the provider level before tool invocation.

The plugin system adds a separate process (the plugin daemon) that communicates with the API server over HTTP. Plugins declare their capabilities via a manifest, are installed as packages, and invocations are proxied through the daemon.

Key architectural decisions:
- **Single output contract**: every tool returns a generator of `ToolInvokeMessage` regardless of type
- **Credential isolation**: per-provider, per-tenant encryption with cache invalidation
- **Parameter form taxonomy**: three forms (LLM-filled, user-form, schema-set) control where values originate
- **Callback-based observability**: separate callback handlers for agent vs. workflow contexts
- **Provider-level discovery**: tools are always accessed through their parent provider

---

## 2. Core Abstractions

### 2.1 Tool Base Class

The abstract `Tool` class (`core/tools/__base/tool.py`) is the root of all tool implementations. Its responsibilities:

1. **Hold entity metadata** (`ToolEntity`) and **runtime context** (`ToolRuntime`)
2. **Type-cast parameters** before invocation using per-parameter type definitions
3. **Provide message factory methods**: `create_text_message`, `create_json_message`, `create_image_message`, `create_blob_message`, `create_file_message`, `create_link_message`, `create_variable_message`
4. **Define the invocation contract**: `_invoke()` returns `ToolInvokeMessage | list[ToolInvokeMessage] | Generator[ToolInvokeMessage]`

The public `invoke()` method wraps `_invoke()` to:
- Merge runtime parameters with explicit parameters
- Cast parameter types according to the tool's parameter schema
- Normalize single/list results into generators

Subclasses override `_invoke()` and `tool_provider_type()`.

### 2.2 ToolProviderController Base Class

The abstract `ToolProviderController` (`core/tools/__base/tool_provider.py`) manages a collection of related tools. Responsibilities:

1. **Hold provider entity** (`ToolProviderEntity`) with identity and credentials schema
2. **Validate credential format** against the declared schema
3. **Vend tool instances** via `get_tool(name)` and `get_tools()`

Each provider type subclass adds its own discovery mechanism (filesystem scan, database query, plugin daemon RPC, MCP server connection).

### 2.3 ToolRuntime

A Pydantic model (`core/tools/__base/tool_runtime.py`) carrying execution context:

| Field | Purpose |
|-------|---------|
| `tenant_id` | Multi-tenant isolation |
| `tool_id` | Specific tool instance reference |
| `invoke_from` | Origin context (debugger, explore, service-api, web-app) |
| `tool_invoke_from` | Whether invoked from workflow, agent, or plugin |
| `credentials` | Decrypted provider credentials |
| `credential_type` | API key vs OAuth2 |
| `runtime_parameters` | Pre-filled parameters (from form/schema) |

The `fork_tool_runtime()` pattern creates new tool instances with different runtime contexts while sharing entity metadata.

### 2.4 ToolEntity and ToolParameter

`ToolEntity` is the declarative schema for a single tool:

- **identity**: name, author, label (i18n), provider reference, icon
- **description**: separate `human` (i18n) and `llm` (plain string) descriptions
- **parameters**: list of `ToolParameter`
- **output_schema**: optional structured output definition
- **has_runtime_parameters**: flag for dynamic parameter providers

`ToolParameter` extends `PluginParameter` with:

- **type**: string, number, boolean, select, secret-input, file, files, checkbox, app-selector, model-selector, dynamic-select, array, object
- **form**: one of three forms that control where the value originates:
  - `LLM` -- filled by the language model at invocation time
  - `FORM` -- filled by the user in the UI before invocation
  - `SCHEMA` -- set at tool configuration time
- **human_description**: shown in UI (i18n)
- **llm_description**: injected into the LLM's tool schema
- **input_schema**: for array/object MCP parameters, stores the raw JSON Schema

---

## 3. Built-in Tool Registry

### 3.1 Filesystem Convention

Built-in tools follow a strict directory convention:

```
core/tools/builtin_tool/providers/
  {provider_name}/
    {provider_name}.yaml      -- Provider identity, credentials schema
    icon.svg                   -- Provider icon
    tools/
      {tool_name}.yaml         -- Tool identity, parameters, descriptions
      {tool_name}.py           -- Python class extending BuiltinTool
```

### 3.2 Provider YAML Schema

A provider YAML declares:

```yaml
identity:
  author: string
  name: string              # must match directory name
  label: {en_US, zh_Hans, ...}
  description: {en_US, zh_Hans, ...}
  icon: icon.svg
  tags: [search, productivity, ...]    # from ToolLabelEnum
credentials_for_provider:
  {credential_name}:
    name: string
    type: secret-input | text-input | select
    required: boolean
    help: {en_US, zh_Hans}
    options: [...]           # for select type
    default: any
```

### 3.3 Tool YAML Schema

Each tool YAML declares:

```yaml
identity:
  name: string
  author: string
  label: {en_US, zh_Hans}
description:
  human: {en_US, zh_Hans}
  llm: string               # what the LLM sees in function-calling schema
parameters:
  - name: string
    type: string | number | boolean | select | file | ...
    required: boolean
    label: {en_US, zh_Hans}
    human_description: {en_US, zh_Hans}
    llm_description: string
    form: llm | form | schema
    default: any
    options:
      - value: string
        label: {en_US, zh_Hans}
```

### 3.4 Discovery and Loading

`BuiltinToolProviderController.__init__()`:

1. Derives provider name from Python module path
2. Loads `{provider}.yaml` from the filesystem (cached via `load_yaml_file_cached`)
3. Parses credentials schema
4. Calls `_load_tools()` which scans the `tools/` subdirectory for YAML files
5. For each tool YAML, dynamically imports the corresponding Python class using `load_single_subclass_from_source()`, which finds the single subclass of `BuiltinTool` in the file
6. Instantiates each tool class with the parsed `ToolEntity`

The `ToolManager` class maintains a singleton cache (`_hardcoded_providers`) of all built-in providers, loaded once at startup with a thread lock.

### 3.5 Position Ordering

A `_positions.py` file controls display order. The `BuiltinToolProviderSort` class reads a position map from the filesystem and sorts providers accordingly for the UI.

### 3.6 Built-in Tool Implementation Pattern

A built-in tool Python file:
- Subclasses `BuiltinTool`
- Implements `_invoke(user_id, tool_parameters, ...)` returning a generator of `ToolInvokeMessage`
- Has access to helper methods: `invoke_model()` for calling LLMs, `summary()` for content summarization, `get_max_tokens()`, `get_prompt_tokens()`

The `summary()` method demonstrates that built-in tools can call LLMs as part of their execution -- they have tenant context and can use the platform's model runtime.

---

## 4. Plugin System Architecture

### 4.1 Plugin Daemon

Dify runs a separate plugin daemon process alongside the API server. Communication is HTTP-based. The daemon:

- Manages plugin lifecycle (install, uninstall, enable, disable)
- Hosts plugin execution sandboxes
- Proxies tool invocations from the API server to plugin code
- Handles credential validation by delegating to plugin code

### 4.2 Plugin Manifest

Plugins declare their capabilities through `PluginDeclaration`, which includes tool providers. Each plugin tool provider entity (`PluginToolProviderEntity`) contains:

- `provider`: provider name
- `plugin_unique_identifier`: globally unique ID
- `plugin_id`: installation-specific ID
- `declaration`: a `ToolProviderEntityWithPlugin` (extends `ToolProviderEntity` with a `tools` list of `ToolEntity`)

### 4.3 PluginToolManager (Client Side)

`PluginToolManager` (`core/plugin/impl/tool.py`) extends `BasePluginClient` and provides:

1. **`fetch_tool_providers(tenant_id)`**: GET to daemon, returns all tool providers for a tenant. Each provider's tools get their provider name prefixed with `{plugin_id}/`.
2. **`invoke(tenant_id, user_id, tool_provider, tool_name, credentials, ...)`**: POST to daemon, streams `ToolInvokeMessage` responses. Handles blob chunk merging.
3. **`validate_provider_credentials(...)`**: POST to daemon, returns boolean.
4. **`get_runtime_parameters(...)`**: POST to daemon, returns dynamic `ToolParameter` list.

### 4.4 PluginTool (Runtime Proxy)

`PluginTool` extends `Tool`. Its `_invoke()`:
1. Converts parameters to plugin format
2. Calls `PluginToolManager.invoke()` with credentials from runtime
3. Yields `ToolInvokeMessage` objects streamed from the daemon

### 4.5 Plugin Installation Flow

`PluginInstaller` handles:
1. **Package upload**: POST binary `.dify_pkg` to daemon
2. **Decode response**: daemon validates and returns `PluginDecodeResponse`
3. **Install task**: daemon installs asynchronously, returns task ID
4. **List/fetch**: standard CRUD operations

The marketplace flow fetches from an external registry, downloads packages, and routes through the same installation pipeline.

### 4.6 Provider Name Namespacing

Plugin providers use `{plugin_id}/{provider_name}` as their canonical name. This prevents collisions between different plugins providing tools with the same name.

---

## 5. Custom Tool Creation (API-Based)

### 5.1 OpenAPI Import Pipeline

Users create custom tools by importing OpenAPI/Swagger specifications:

1. **Schema parsing**: `ApiBasedToolSchemaParser.auto_parse_to_tool_bundle()` accepts raw YAML/JSON, auto-detects format (OpenAPI 3.x, Swagger 2.x, OpenAI plugin, OpenAI actions), and produces a list of `ApiToolBundle` objects
2. **Bundle structure**: Each `ApiToolBundle` captures server URL, HTTP method, operation ID, extracted parameters, and the raw OpenAPI operation dict
3. **Parameter extraction**: Path params, query params, header params, and request body properties are converted to `ToolParameter` objects with appropriate types
4. **Provider creation**: An `ApiToolProvider` database record stores the schema, credentials, and bundles (JSON-serialized)

### 5.2 ApiToolBundle

The intermediate representation between OpenAPI spec and tool entity:

| Field | Purpose |
|-------|---------|
| `server_url` | Base URL from spec |
| `method` | HTTP method |
| `summary` | Operation summary (becomes tool description) |
| `operation_id` | Becomes tool name |
| `parameters` | Extracted `ToolParameter` list |
| `openapi` | Raw operation dict for request assembly |
| `output_schema` | Response schema (optional) |

### 5.3 ApiTool Invocation

`ApiTool._invoke()`:
1. Calls `assembling_request()` to build headers (including auth)
2. Calls `do_http_request()` which:
   - Separates parameters into path, query, header, cookie, and body
   - Handles file uploads (multipart)
   - Replaces path parameters in URL
   - Serializes body based on content type
   - Uses SSRF proxy for all outbound requests
3. Parses response: JSON responses become `create_json_message`, text becomes `create_text_message`

### 5.4 Authentication Types

Three auth modes for API tools:
- **None**: no auth headers
- **API Key Header**: adds a configurable header (default `Authorization`) with configurable prefix (Basic/Bearer/Custom)
- **API Key Query**: adds key as a query parameter

Credentials are stored encrypted in the `ApiToolProvider` model.

---

## 6. MCP Tool Integration

### 6.1 Architecture

MCP tools connect to external MCP servers over SSE/HTTP. The `MCPToolProviderController`:
- Stores server URL, headers, timeout configuration
- Converts remote MCP tool definitions to internal `ToolEntity` format
- Creates `MCPTool` instances that proxy invocations

### 6.2 MCPTool Invocation

`MCPTool._invoke()`:
1. Strips None/empty parameters
2. Loads provider entity from DB to get decrypted server URL and headers
3. Retrieves OAuth tokens if available
4. Creates `MCPClientWithAuthRetry` connection
5. Calls `mcp_client.invoke_tool()` with tool name and args
6. Converts MCP `CallToolResult` content types to `ToolInvokeMessage`:
   - `TextContent` -> attempts JSON parse, falls back to text
   - `ImageContent`/`AudioContent` -> blob message with mime type
   - `EmbeddedResource` -> text or blob depending on resource type
7. Handles structured output via `create_variable_message()`

### 6.3 Parameter Conversion

`ToolTransformService.convert_mcp_schema_to_parameter()` converts MCP `inputSchema` (JSON Schema) into Dify `ToolParameter` objects. Array and object types use the `input_schema` field to preserve the full JSON Schema.

---

## 7. Workflow-as-Tool

### 7.1 Concept

Any published workflow can be exposed as a tool for use in other workflows or agents. `WorkflowToolProviderController` wraps a workflow app.

### 7.2 WorkflowTool Invocation

`WorkflowTool._invoke()`:
1. Loads the target `App` and `Workflow` from the database
2. Transforms tool parameters, separating file parameters from regular ones
3. Invokes `WorkflowAppGenerator.generate()` with `streaming=False`
4. Extracts outputs, files, and LLM usage metadata from the result
5. Yields variable messages for each non-reserved output key
6. Yields text and JSON messages with the full outputs

### 7.3 Call Depth Tracking

Workflow tools track `workflow_call_depth` to prevent infinite recursion. Each nested invocation increments the depth counter. The system enforces a maximum depth.

### 7.4 Parameter Configuration

Workflow tool parameters are defined through `WorkflowToolParameterConfiguration`:
- `name`: maps to workflow input variable
- `description`: for LLM context
- `form`: LLM-filled or user-form (same taxonomy as other tools)

---

## 8. Tool Invocation Pipeline

### 8.1 ToolEngine

`ToolEngine` is the central dispatcher with two entry points:

#### Agent Invocation (`agent_invoke`)

1. Parse string parameters to dict (single-param shortcut: if tool has one LLM param, wrap string as `{param_name: value}`)
2. Fire `agent_tool_callback.on_tool_start()`
3. Call `_invoke()` which:
   - Records start time
   - Calls `tool.invoke()` generator
   - Catches exceptions, wraps in `ToolEngineInvokeError` with metadata
   - Yields `ToolInvokeMeta` at the end with timing info
4. Transform file messages (upload tool-generated files to storage)
5. Extract binary data and create `MessageFile` records
6. Convert all messages to plain text for LLM consumption
7. Fire `agent_tool_callback.on_tool_end()`
8. Return `(plain_text, message_file_ids, meta)`

Error handling returns error strings instead of raising, keeping the agent loop alive.

#### Workflow Invocation (`generic_invoke`)

1. Fire `workflow_tool_callback.on_tool_start()`
2. Merge runtime parameters
3. Handle `WorkflowTool` call depth tracking
4. Call `tool.invoke()` directly
5. Pass response through `workflow_tool_callback.on_tool_execution()`
6. Return the generator (streaming)

### 8.2 ToolManager Orchestration

`ToolManager` is the top-level coordinator. Key methods:

#### `get_tool_runtime(tenant_id, provider_type, provider_id, tool_name, invoke_from, ...)`

The universal tool resolution method:
1. Routes by `provider_type`:
   - **BUILT_IN**: loads hardcoded provider, gets tool, loads encrypted credentials from DB cache, creates runtime
   - **PLUGIN**: fetches from plugin daemon, resolves credentials (enterprise credential system or direct)
   - **API**: loads `ApiToolProvider` from DB, decrypts credentials, assembles tool bundles, finds named tool
   - **WORKFLOW**: loads `WorkflowToolProvider` from DB, instantiates `WorkflowTool` with app/workflow refs
   - **MCP**: loads `MCPToolProvider` from DB via `MCPToolManageService`
2. Attaches `ToolRuntime` with decrypted credentials
3. Returns a ready-to-invoke `Tool` instance

#### `get_agent_tool_runtime(tenant_id, app_id, agent_tool, invoke_from)`

Wrapper for agent context: extracts provider info from `AgentToolEntity`, calls `get_tool_runtime()`.

#### `get_workflow_tool_runtime(tenant_id, app_id, node_id, node_data, invoke_from, variable_pool)`

Wrapper for workflow context: extracts from `ToolNodeData`, resolves variable references in tool configurations, calls `get_tool_runtime()`.

### 8.3 Workflow Tool Node

`ToolNode` (`core/workflow/nodes/tool/tool_node.py`) is the workflow graph node:

1. Calls `ToolManager.get_workflow_tool_runtime()` to get a configured tool
2. Calls `_generate_parameters()` to resolve parameter values from the variable pool:
   - `variable` type: direct variable reference
   - `mixed`/`constant`: template string with variable interpolation
3. Calls `ToolEngine.generic_invoke()`
4. In `_transform_message()`: accumulates text, files, JSON, and variable outputs into a `NodeRunResult`
5. Streams `StreamChunkEvent` for text chunks, yields `StreamCompletedEvent` with final result

### 8.4 Agent Tool Binding

Agents bind tools via `AgentToolEntity`:
- `provider_type`, `provider_id`, `tool_name`: identify the tool
- `tool_parameters`: pre-filled form/schema parameters
- `credential_id`: optional enterprise credential reference

The agent runtime resolves each bound tool through `ToolManager.get_agent_tool_runtime()` and presents them to the LLM as function definitions.

---

## 9. Credential Management

### 9.1 Encryption

Credentials are encrypted using a tenant-specific key via `ProviderConfigEncrypter`:
1. Each credential field is encrypted individually based on its declared type (SECRET_INPUT gets encrypted, TEXT_INPUT stored as-is)
2. Encrypted values are stored in the database alongside the provider record
3. A cache layer (`SingletonProviderCredentialsCache` / `ToolProviderCredentialsCache`) avoids repeated decryption

### 9.2 Storage Models

| Model | Provider Type | Key Fields |
|-------|--------------|------------|
| `BuiltinToolProvider` | built-in/plugin | tenant_id, provider, encrypted_credentials |
| `ApiToolProvider` | API (custom) | tenant_id, name, schema_type, schema, credentials_str, tools (JSON) |
| `WorkflowToolProvider` | workflow | tenant_id, app_id, name, version, parameters (JSON) |
| `MCPToolProvider` | MCP | tenant_id, name, server_url, headers, timeout config |
| `ToolOAuthSystemClient` | OAuth (system) | provider, client_id, client_secret |
| `ToolOAuthTenantClient` | OAuth (tenant) | provider, tenant_id, credentials_str |

### 9.3 Validation Flow

1. User submits credentials through the API
2. `ToolProviderController.validate_credentials_format()` checks types against schema
3. Provider-specific `_validate_credentials()` performs live validation (e.g., makes a test API call)
4. On success, credentials are encrypted and stored

### 9.4 Enterprise Credential System

For plugin tools, Dify supports an enterprise credential model where credentials are managed centrally:
- `PluginCredentialType` distinguishes between direct and enterprise-managed credentials
- `credential_id` on tool entities references centrally managed credential sets
- Resolution happens in `ToolManager.get_tool_runtime()` via `PluginManagerService`

---

## 10. Tool Categories and Organization

### 10.1 Label System

Tools are categorized using `ToolLabelEnum`:
- search, image, videos, weather, finance, design, travel, social, news, medical, productivity, education, business, entertainment, utilities, rag, other

### 10.2 Label Binding

`ToolLabelBinding` model associates tools with labels. `ToolLabelManager` manages these bindings and provides filtered queries.

### 10.3 Provider Types in UI

The frontend `CollectionType` enum maps to backend `ToolProviderType`:
- `builtIn` (builtin) -- hardcoded + plugin (displayed together)
- `custom` (api) -- user-created via OpenAPI import
- `workflow` -- workflow-as-tool
- `mcp` -- MCP server connections
- `datasource` -- data retrieval tools
- `trigger` -- event-triggered tools

### 10.4 Icon System

Icons are resolved differently per provider type:
- **Built-in**: served from API endpoint `/console/api/workspaces/current/tool-provider/builtin/{name}/icon`
- **Plugin**: served via plugin service with tenant-scoped URLs
- **API/Workflow**: stored as JSON `{background: color, content: emoji}` in database
- **MCP**: stored as string URL or icon reference

---

## 11. Frontend Tool Components

### 11.1 Tool Parameter Forms

The frontend renders parameter forms based on the `form` field:
- `LLM` parameters are NOT shown in configuration UI (filled by the model at runtime)
- `FORM` parameters render as input fields matching their type (text, number, select, checkbox, file upload, etc.)
- `SCHEMA` parameters are set at tool-provider configuration time

### 11.2 Workflow Tool Node UI

Located at `web/app/components/workflow/nodes/tool/`:
- `panel.tsx`: configuration panel for the tool node
- `node.tsx`: canvas representation
- `use-config.ts`: React hook managing tool selection and parameter state
- `components/tool-form/`: parameter input components
- `types.ts`: TypeScript type definitions mirroring backend entities

The node UI allows:
1. Selecting a tool provider and specific tool
2. Configuring parameters with three input modes: variable reference, constant, or mixed (template)
3. Viewing output schema

### 11.3 Tool Provider Management

- `edit-custom-collection-modal/`: UI for creating/editing API tool collections (OpenAPI import)
- `provider/`: tool provider list and detail views
- `setting/`: credential configuration forms
- `mcp/`: MCP server connection management
- `marketplace/`: plugin marketplace browsing and installation

### 11.4 Chatbot Tool Configuration

Located at `web/app/components/app/configuration/tools/`:
- Allows selecting which tools are available to the agent
- Configures form/schema parameters
- Each selected tool becomes an `AgentToolEntity` in the app configuration

---

## 12. Key Patterns for Reimplementation

### 12.1 Provider-Tool Hierarchy

Every tool belongs to a provider. Credentials exist at the provider level. Tools within a provider share credentials. This two-level structure should be preserved as it simplifies credential management and tool organization.

### 12.2 Unified Output Contract

All tools produce `ToolInvokeMessage` generators. Message types include: text, JSON, image, blob, link, file, variable, log, retriever-resources. This uniform interface allows the engine to handle any tool output generically. The `variable` type is particularly important for structured outputs that feed into downstream workflow nodes.

### 12.3 Parameter Form Taxonomy

The LLM/FORM/SCHEMA distinction is elegant:
- **LLM**: the parameter appears in the function-calling schema sent to the model
- **FORM**: the user fills it in before execution (runtime configuration)
- **SCHEMA**: set at tool installation/configuration time (provider-level defaults)

This determines both UI rendering and invocation-time parameter resolution.

### 12.4 Fork-Based Tool Instantiation

Tools are instantiated once with their entity metadata, then `fork_tool_runtime()` creates copies with different runtime contexts. This avoids re-parsing YAML/loading classes per invocation while keeping runtime state isolated.

### 12.5 Callback-Based Observability

Separate callback handlers for agent (`DifyAgentCallbackHandler`) and workflow (`DifyWorkflowCallbackHandler`) contexts allow different tracing, logging, and UI update behaviors without coupling the tool engine to specific execution contexts.

### 12.6 SSRF Protection

All outbound HTTP requests from API tools go through an SSRF proxy, preventing tools from accessing internal network resources. This is critical for multi-tenant security.

### 12.7 Credential Encryption Pattern

Per-tenant encryption keys, per-field encryption based on schema type, with a caching layer. The cache uses a singleton pattern keyed by (tenant_id, provider_type, provider_identity).

### 12.8 Dynamic Parameters

Tools can declare `has_runtime_parameters: true`, causing the system to fetch parameters at invocation time rather than relying solely on static YAML definitions. Plugin tools and MCP tools use this for dynamic parameter discovery.

---

## 13. Database Schema Summary

Key tables/models for tool persistence:

| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| `builtin_tool_providers` | Stores per-tenant credentials for built-in providers | tenant_id, provider name |
| `api_tool_providers` | Stores custom API tool definitions and credentials | tenant_id; contains serialized schema + tool bundles |
| `workflow_tool_providers` | Stores workflow-as-tool configurations | tenant_id, app_id (references workflow app) |
| `mcp_tool_providers` | Stores MCP server connections | tenant_id, server_url, encrypted headers |
| `tool_label_bindings` | Many-to-many between tools and labels | tool_id, label_name |
| `tool_files` | Files generated by tool invocations | tool_id, file metadata |
| `tool_model_invokes` | Records of LLM calls made by built-in tools | tool_name, model, tokens, timing |
| `tool_conversation_variables` | Per-conversation tool state | conversation_id, variables_str |
| `tool_oauth_system_clients` | System-level OAuth client configs | provider, client_id |
| `tool_oauth_tenant_clients` | Tenant-level OAuth tokens | provider, tenant_id, credentials |

---

## 14. Differences: Workflow Tool Node vs Agent Tool Binding

| Aspect | Workflow Tool Node | Agent Tool Binding |
|--------|--------------------|--------------------|
| Parameter resolution | Variable pool references, templates | LLM-generated at runtime |
| Output handling | Structured (text, json, files, variables per key) | Flattened to plain text + file IDs |
| Error handling | Node failure status, stops execution | Error string returned to LLM, loop continues |
| Streaming | Generator-based, yields node events | Collected into final result |
| Call depth | Tracked and limited | Not applicable |
| Configuration | Per-node in workflow graph | Per-app agent configuration |
| Form parameters | Resolved from variable pool or constants | Pre-configured in app settings |

---

## 15. Reimplementation Recommendations

### 15.1 Start With

1. **Base abstractions**: `Tool`, `ToolProvider`, `ToolRuntime`, `ToolInvokeMessage` -- these are small and well-defined
2. **Built-in tool registry**: YAML-based discovery is simple and effective
3. **API tool import**: OpenAPI parsing to tool bundles is self-contained
4. **Credential encryption**: standard pattern, can use any encryption library

### 15.2 Defer

1. **Plugin daemon**: significant infrastructure; consider using MCP servers instead for extensibility
2. **Workflow-as-tool**: requires a full workflow engine first
3. **Enterprise credential management**: can start with simple per-provider credentials

### 15.3 Adapt for MCP-First Architecture

Since NYQST already uses MCP as its extensibility protocol, consider:
- Using MCP servers in place of Dify's plugin daemon
- Mapping the provider-tool hierarchy to MCP server-tool hierarchy
- Preserving the parameter form taxonomy (LLM/FORM/SCHEMA) as it maps well to MCP's `inputSchema`
- Adapting the credential system for MCP server authentication

### 15.4 Key Interfaces to Preserve

1. `Tool._invoke(user_id, tool_parameters, ...) -> Generator[ToolInvokeMessage]`
2. `ToolProvider.get_tool(name) -> Tool`
3. `ToolManager.get_tool_runtime(tenant_id, provider_type, ...) -> Tool`
4. `ToolEngine.agent_invoke(tool, params, ...) -> (text, files, meta)`
5. `ToolEngine.generic_invoke(tool, params, ...) -> Generator[ToolInvokeMessage]`

These five interfaces define the entire tool system contract.

---

## 16. Appendix: Provider Type Comparison

| Feature | Built-in | Plugin | API (Custom) | Workflow | MCP |
|---------|----------|--------|-------------|----------|-----|
| Discovery | Filesystem scan | Daemon RPC | Database | Database | Database + remote |
| Credentials | DB (encrypted) | DB + daemon | DB (encrypted) | None | DB + OAuth |
| Invocation | Direct Python | HTTP to daemon | HTTP to external | Internal workflow engine | SSE/HTTP to MCP server |
| Parameter source | YAML | Plugin manifest | OpenAPI spec | Workflow inputs | MCP inputSchema |
| Can call LLMs | Yes (built-in) | Yes (via daemon) | No | Yes (via workflow) | No |
| Sandbox | No | Daemon sandbox | SSRF proxy | Workflow limits | SSRF proxy |
| Extensible by users | No | Marketplace install | OpenAPI import | Build workflow | Add MCP server URL |
