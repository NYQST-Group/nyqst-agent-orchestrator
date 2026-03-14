# 14 - Dify Frontend State Management Architecture

> Deep analysis for clean-room reimplementation. Describes patterns and architecture,
> not implementation details.

## 1. State Management Overview

Dify's frontend uses a **multi-layer state architecture** with four complementary
systems, each handling a different category of state:

| Layer | Technology | Scope | Purpose |
|-------|-----------|-------|---------|
| Server state | TanStack React Query v5 | Global (via QueryClientProvider) | API data fetching, caching, revalidation |
| Client state (complex) | Zustand (vanilla + react) | Scoped via React Context | Workflow editor, form inputs, UI panels |
| Client state (simple) | Zustand (create) | Global singletons | App detail, plugins, tags, access control |
| Client state (minimal) | Jotai atoms | Component-local | Marketplace search/filter/sort |
| URL state | nuqs (useQueryState) | URL search params | Marketplace filters (when URL persistence needed) |
| Context propagation | React Context (use-context-selector) | Subtree | Auth, workspace, provider config, modals |
| Event bus | ahooks useEventEmitter | Subtree | Cross-component notifications |
| Undo/redo | zundo (temporal middleware) | Workflow history | Node/edge history with deep equality checks |

There is **no SWR** usage. The codebase has fully migrated to TanStack React Query.
Jotai is used minimally (marketplace only). The primary client state tool is Zustand.

---

## 2. Provider Hierarchy (Component Tree)

The root layout establishes the provider nesting order. Understanding this is critical
for reimplementation because it defines what state is available where.

### Root layout (`app/layout.tsx`)

```
SerwistProvider (service worker)
  JotaiProvider (atoms)
    ThemeProvider (next-themes)
      NuqsAdapter (URL state)
        BrowserInitializer
          SentryInitializer
            TanstackQueryInitializer    <-- QueryClientProvider
              I18nServerProvider
                ToastProvider
                  GlobalPublicStoreProvider  <-- system features gate
                    {children}
```

### Authenticated layout (`app/(commonLayout)/layout.tsx`)

```
AppInitializer                         <-- guards setup/login status
  AppContextProvider                   <-- user profile, workspace, role
    EventEmitterContextProvider        <-- cross-component events
      ProviderContextProvider          <-- model providers, billing, plan
        ModalContextProvider           <-- modal stack management
          Header
          {children}
```

### Workflow editor (nested further inside app pages)

```
WorkflowContextProvider               <-- mega Zustand store via Context
  WorkflowHistoryProvider             <-- zundo undo/redo store
    HooksStoreProvider                <-- callback registry store
      DatasetsDetailProvider
        FeaturesProvider
          {workflow UI}
```

### Shared web app routes (`app/(shareLayout)`)

```
WebAppStoreProvider                    <-- share code, app info, access mode
  {chat/completion/workflow embeds}
```

**Key insight**: The authenticated and shared layouts are entirely separate subtrees.
They share only the root providers (Query Client, Toast, GlobalPublicStore).

---

## 3. Zustand Stores Catalogue

### 3.1 Global Singleton Stores

These use `create()` directly and exist as module-level singletons. Any component
can import and use them without a provider.

#### GlobalPublicStore
- **File**: `context/global-public-context.tsx`
- **State**: `systemFeatures` (branding, auth methods, feature flags)
- **Pattern**: Hybrid -- Zustand store + TanStack Query. The query fetcher writes
  into the Zustand store via `getState().setSystemFeatures()`. This allows both
  React Query cache and synchronous Zustand access.
- **Gate**: Wraps children in a loading spinner until system features are fetched.

#### AppStore
- **File**: `app/components/app/store.ts`
- **State**: `appDetail`, `appSidebarExpand`, `currentLogItem`, `currentLogModalActiveTab`,
  modal visibility flags (prompt log, agent log, message log, features config)
- **Pattern**: Simple state + setters. Used across the app detail/configuration pages.

#### AccessControlStore
- **File**: `context/access-control-store.ts`
- **State**: `appId`, `specificGroups`, `specificMembers`, `currentMenu`,
  `selectedGroupsForBreadcrumb`
- **Pattern**: Simple state + setters for the access control panel.

#### WebAppStore
- **File**: `context/web-app-context.tsx`
- **State**: `shareCode`, `appInfo`, `appParams`, `webAppAccessMode`, `appMeta`,
  `userCanAccessApp`, `embeddedUserId`, `embeddedConversationId`
- **Pattern**: Global Zustand store + a provider component that syncs URL params
  (pathname, search params) into the store on mount/change.

#### PluginDetailPanelStore
- **File**: `app/components/plugins/plugin-detail-panel/store.ts`
- **State**: `detail` (selected plugin for detail panel)

#### ReadmePanelStore
- **File**: `app/components/plugins/readme-panel/store.ts`
- **State**: `currentPluginDetail` with `showType` (drawer vs modal)

#### PluginFilterStore
- **File**: `app/components/plugins/plugin-page/filter-management/store.ts`
- **State**: `tagList`, `categoryList`, modal visibility flags

#### TagManagementStore
- **File**: `app/components/base/tag-management/store.ts`
- **State**: `tagList`, `showTagManagementModal`

#### ToolLabelsStore
- **File**: `app/components/tools/labels/store.ts`
- **State**: `labelList`

#### PluginDependencyStore
- **File**: `app/components/workflow/plugin-dependency/store.ts`
- **State**: `dependencies` array

#### TriggerStatusStore
- **File**: `app/components/workflow/store/trigger-status.ts`
- **State**: `triggerStatuses` (Record of nodeId to enabled/disabled)
- **Pattern**: Uses `subscribeWithSelector` middleware for fine-grained subscriptions.

### 3.2 Context-Scoped Stores (created per instance via React Context)

These use `createStore()` from `zustand/vanilla`, wrap the result in a React Context,
and provide a custom `useStore(selector)` hook. This pattern allows multiple
independent instances (e.g., multiple workflow editors) without store collision.

#### Workflow Store (the mega-store)
- **File**: `app/components/workflow/store/workflow/index.ts`
- **Pattern**: Slice-based composition. A single vanilla store is created by merging
  13+ slices via spread. Provided through `WorkflowContext`.
- **Injection**: Supports `injectWorkflowStoreSliceFn` for page-specific extensions
  (WorkflowApp slice, RAG Pipeline slice).
- **Access**: `useStore(selector)` hook + `useWorkflowStore()` for raw store API.

##### Workflow Store Slices:

| Slice | File | Manages |
|-------|------|---------|
| **WorkflowSlice** | `workflow-slice.ts` | Running data, listening state, clipboard, selection rect, control mode (pointer/hand), mouse position, confirm dialogs, DSL import modal, file upload config |
| **WorkflowDraftSlice** | `workflow-draft-slice.ts` | Backup draft (nodes/edges/viewport/features/env vars), debounced sync (5s), sync hash, sync status, data loaded flag |
| **NodeSlice** | `node-slice.ts` | Single-run panel, node animation, candidate node, node context menu, variable assignment popup, connecting/entering node state, iteration/loop counters |
| **PanelSlice** | `panel-slice.ts` | Panel widths, visibility flags for features/version-history/inputs/debug-preview panels, context menus, variable inspect panel |
| **LayoutSlice** | `layout-slice.ts` | Canvas dimensions, right/node/preview/other/bottom panel widths/heights, variable inspect panel height, maximize canvas flag. Persists several values to localStorage. |
| **HistorySlice** | `history-slice.ts` | Historical workflow data, run history visibility, version history list |
| **VersionSlice** | `version-slice.ts` | Draft/published timestamps, current version, restoring flag |
| **ToolSlice** | `tool-slice.ts` | Tool published flag, user input flag, tool lists (built-in, custom, workflow, MCP) |
| **FormSlice** | `form-slice.ts` | Run form inputs (key-value), uploaded files |
| **EnvVariableSlice** | `env-variable-slice.ts` | Environment variables list, secrets, panel visibility. Implements mutex: showing env panel hides debug/chat/global panels. |
| **ChatVariableSlice** | `chat-variable-slice.ts` | Conversation variables, chat/global variable panel visibility. Same mutex pattern. |
| **HelpLineSlice** | `help-line-slice.ts` | Alignment guide positions (horizontal/vertical) for drag snapping |
| **InspectVarsSlice** | `debug/inspect-vars-slice.ts` | Variable inspector state. Uses immer `produce()` for immutable nested updates on node variable arrays. Most complex slice with operations: set, delete, rename, reset, per-node and per-var granularity. |

##### Injected Slices:

| Slice | Injected by | Manages |
|-------|------------|---------|
| **WorkflowAppSlice** | `workflow-app/store/workflow/workflow-slice.ts` | `appId`, `appName`, onboarding state, node default configs, start node selection |
| **RagPipelineSlice** | `rag-pipeline/store/index.ts` | Pipeline ID, knowledge name/icon, input field panels, node configs, pipeline variables, data source list |

#### HooksStore
- **File**: `app/components/workflow/hooks-store/store.ts`
- **Pattern**: A store of **callback functions**, not data. Created via `createStore()`
  with defaults of `noop`. Components inject real implementations via `refreshAll()`.
- **Purpose**: Decouples workflow operations (sync draft, run, stop, export, backup,
  restore, inspect vars) from the UI tree. The workflow panel calls
  `useHooksStore(s => s.handleRun)` without knowing which page provides the implementation.
- **Functions registered**: `doSyncWorkflowDraft`, `handleRefreshWorkflowDraft`,
  `handleBackupDraft`, `handleLoadBackupDraft`, `handleRestoreFromPublishedWorkflow`,
  `handleRun`, `handleStopRun`, `handleStartWorkflowRun`,
  `handleWorkflowStartRunInWorkflow/Chatflow`, various trigger handlers,
  `fetchInspectVars`, `editInspectVarValue`, and ~15 more.

#### WorkflowHistoryStore
- **File**: `app/components/workflow/workflow-history-store.tsx`
- **Pattern**: Zustand + `zundo` temporal middleware for undo/redo.
- **State**: `nodes`, `edges`, `workflowHistoryEvent`, `workflowHistoryEventMeta`
- **Undo**: Uses `fast-deep-equal` for equality checking to avoid spurious history entries.
- **Access**: Custom `useWorkflowHistoryStore()` returns `{ store, shortcutsEnabled, setShortcutsEnabled }`.

#### FeaturesStore
- **File**: `app/components/base/features/store.ts`
- **Pattern**: `createStore()` factory with default feature flags.
- **State**: Feature toggles (moreLikeThis, opening, suggested, text2speech,
  speech2text, citation, moderation, file/image config, annotationReply) + modal visibility.

#### FileUploaderStore
- **File**: `app/components/base/file-uploader/store.tsx`
- **Pattern**: Context-scoped with external sync. Provider accepts `value` and `onChange`
  props. Uses `useEffect` to sync external value changes into the store (with deep
  equality check via es-toolkit `isEqual`).
- **State**: `files` array, `setFiles` (also triggers `onChange` callback)

#### DatasetImageUploaderStore
- **File**: `app/components/datasets/common/image-uploader/store.tsx`
- **Pattern**: Same as FileUploaderStore but without external sync effect.

#### DataSourceStore
- **File**: `app/components/datasets/documents/create-from-pipeline/data-source/store/index.ts`
- **Pattern**: Slice-based composition (same as workflow store pattern).
- **Slices**: Common, LocalFile, OnlineDocument, WebsiteCrawl, OnlineDrive

#### DatasetsDetailStore
- **File**: `app/components/workflow/datasets-detail-store/store.ts`
- **State**: `datasetsDetail` (Record<id, DataSet>). Uses immer for merge updates.

#### NoteEditorStore
- **File**: `app/components/workflow/note-node/note-editor/store.ts`
- **State**: Rich text editor state (bold, italic, strikethrough, link, bullet selection
  flags, link anchor element, link URL).

#### VisualEditorStore
- **File**: `app/components/workflow/nodes/llm/components/json-schema-config-modal/visual-editor/store.ts`
- **State**: `hoveringProperty`, `isAddingNewField`, `advancedEditing`, `backupSchema`

---

## 4. TanStack React Query (Server State)

### 4.1 Setup

- Single `QueryClient` created via `makeQueryClient()`, shared across the app.
- On server: new client per request. On browser: singleton (created once, reused).
- DevTools loaded via `TanStackDevtoolsLoader` (lazy/dynamic).

### 4.2 Query Key Convention

All query hooks use a namespace-prefixed key pattern:

```
[namespace, entity, ...params]
```

Examples from `use-common.ts`:
- `['common', 'user-profile']`
- `['common', 'current-workspace']`
- `['common', 'model-list', ModelTypeEnum]`
- `['common', 'model-parameter-rules', provider, model]`

Keys are defined as `const` tuples with `as const` for type safety. Factory functions
generate parameterized keys: `commonQueryKeys.modelList(type)`.

Each domain has its own `use-*.ts` service file with a local `NAME_SPACE`:
- `use-common.ts` - user, workspace, models, integrations
- `use-apps.ts` - app CRUD
- `use-workflow.ts` - workflow operations
- `use-plugins.ts` - plugin marketplace
- `use-share.ts` - shared/embedded app data
- `use-billing.ts` - plan and usage
- `use-education.ts` - education program status
- `use-tools.ts`, `use-models.ts`, `use-triggers.ts`, `use-strategy.ts`,
  `use-datasource.ts`, `use-endpoints.ts`, `use-log.ts`, `use-oauth.ts`,
  `use-pipeline.ts`, `use-plugins-auth.ts`, `use-dataset-card.ts`
- `knowledge/use-document.ts`, `knowledge/use-metadata.ts`, `knowledge/use-segment.ts`,
  `knowledge/use-dataset.ts`, `knowledge/use-import.ts`, `knowledge/use-hit-testing.ts`,
  `knowledge/use-create-dataset.ts`

### 4.3 Invalidation Pattern

Two approaches to cache invalidation:

1. **Direct**: `queryClient.invalidateQueries({ queryKey: [...] })` -- used in context
   providers where the query client is already available.

2. **Hook-based**: `useInvalid(key)` utility from `use-base.ts` returns a callback
   that invalidates the given key. Used in components that need to trigger refresh
   from event handlers.

3. **Reset**: `useReset(key)` utility returns a callback that resets query data
   (removes cached data entirely, not just marks stale).

### 4.4 Mutations

Mutations use `useMutation` with explicit `mutationKey` for tracking. Examples:
registration flows, structured output generation, logout. Mutations do not
auto-invalidate; the caller must handle cache updates.

---

## 5. React Context Layer (Non-Zustand)

These contexts use `use-context-selector` (not standard React context) to enable
fine-grained re-render control via selector functions.

### AppContext
- **Provided by**: `AppContextProvider`
- **Data**: `userProfile`, `currentWorkspace`, role booleans (`isCurrentWorkspaceManager`,
  `isCurrentWorkspaceOwner`, `isCurrentWorkspaceEditor`, `isCurrentWorkspaceDatasetOperator`),
  `langGeniusVersionInfo`
- **Server data**: Fetched via `useUserProfile()`, `useCurrentWorkspace()`,
  `useLangGeniusVersion()` (all TanStack Query hooks).
- **Invalidation**: Exposes `mutateUserProfile()` and `mutateCurrentWorkspace()` which
  call `queryClient.invalidateQueries()`.
- **Optimization**: Uses `useMemo` for all derived values. Exposes `useSelector` for
  fine-grained context selection.

### ProviderContext
- **Provided by**: `ProviderContextProvider`
- **Data**: `modelProviders`, `textGenerationModelList`, `supportRetrievalMethods`,
  `isAPIKeySet`, `plan`, billing/education/license state, feature flags
- **Pattern**: Mixes TanStack Query (for model data) with `useState` + imperative
  `fetchCurrentPlanInfo()` for billing. This is a transitional pattern -- billing
  hasn't been migrated to React Query yet.
- **Optimization**: Uses `useContextSelector` for consumers that only need one field.

### WorkspaceContext
- **Data**: `workspaces` list (all workspaces the user belongs to)
- **Pattern**: Simple React Context wrapping a TanStack Query hook.

### EventEmitterContext
- **Data**: A shared `EventEmitter<string>` instance from ahooks.
- **Pattern**: Used for cross-component event broadcasting without prop drilling.
  Events are string-typed.

### ModalContext
- **Data**: Modal stack management (not analyzed in detail).

---

## 6. Real-Time State (SSE Stream Handling)

### 6.1 SSE Architecture

Dify does **not** use browser `EventSource` or third-party SSE libraries. Instead,
it implements custom SSE via `fetch()` + `ReadableStream` reader.

The core function is `ssePost()` in `service/base.ts`:

1. Makes a POST request with streaming response
2. Gets a `ReadableStream` reader from `response.body`
3. Reads chunks via `reader.read()` in a recursive loop
4. Decodes UTF-8 text, splits by newlines, parses `data:` prefixed JSON lines
5. Dispatches to typed callback handlers based on `event` field

### 6.2 SSE Event Types and Callbacks

The `IOtherOptions` type defines ~25 callback handlers:

- **Chat events**: `onData`, `onThought`, `onFile`, `onMessageEnd`, `onMessageReplace`,
  `onAnnotationReply`
- **Workflow events**: `onWorkflowStarted`, `onWorkflowFinished`, `onNodeStarted`,
  `onNodeFinished`, `onNodeRetry`
- **Iteration events**: `onIterationStart`, `onIterationNext`, `onIterationFinish`
- **Loop events**: `onLoopStart`, `onLoopNext`, `onLoopFinish`
- **Parallel events**: `onParallelBranchStarted`, `onParallelBranchFinished`
- **Text events**: `onTextChunk`, `onTextReplace`
- **TTS events**: `onTTSChunk`, `onTTSEnd`
- **Agent events**: `onAgentLog`
- **Pipeline events**: `onDataSourceNodeProcessing`, `onDataSourceNodeCompleted`,
  `onDataSourceNodeError`
- **Lifecycle**: `onCompleted`, `onError`

### 6.3 SSE to Store Update Flow

The typical pattern for SSE events updating Zustand state:

1. Component calls `ssePost()` with callback handlers
2. Callbacks reference Zustand store setters (e.g., `workflowStore.getState().setWorkflowRunningData()`)
3. Store update triggers re-render of subscribed components

For workflow runs specifically:
- `onWorkflowStarted` initializes `workflowRunningData`
- `onNodeStarted`/`onNodeFinished` update node execution state
- `onWorkflowFinished` finalizes the running data
- `onError` triggers error display

### 6.4 Auth Retry in SSE

If `ssePost()` receives a 401 response, it calls `refreshAccessTokenOrRelogin()` and
recursively retries the same `ssePost()` call. This creates automatic token refresh
for long-running SSE connections.

---

## 7. Authentication State

### 7.1 Token Management

- **Cookie-based**: Auth tokens stored in HTTP-only cookies (not in JS-accessible state).
- **CSRF**: A CSRF token is read from a cookie (`CSRF_COOKIE_NAME`) and sent as a
  header (`CSRF_HEADER_NAME`) on API requests.
- **Refresh**: `refresh-token.ts` implements cross-tab safe token refresh:
  - Uses `localStorage` lock (`is_other_tab_refreshing`) to prevent concurrent refreshes
  - Includes `last_refresh_time` for staleness detection
  - Registers `beforeunload` handler to release lock on page close
  - Race condition protection: waits if another tab is refreshing, with timeout

### 7.2 Login State Detection

- `useIsLogin()` TanStack Query hook: tries to GET `/account/profile`. If it succeeds,
  the user is logged in. Any error means not logged in.
- `staleTime: 0, gcTime: 0` ensures fresh check every time.

### 7.3 Web App Auth (Shared/Embedded)

Separate auth flow for public-facing web apps:
- `getWebAppPassport()` provides a passport token
- Sent via `PASSPORT_HEADER_NAME` header
- Web app SSO redirect handled by `requiredWebSSOLogin()` which preserves the
  current URL as a redirect parameter

---

## 8. Workspace/Tenant Context Propagation

### 8.1 Current Workspace

The `AppContextProvider` fetches the current workspace via `POST /workspaces/current`
and provides it to the entire authenticated subtree. Components access workspace data
via:

- `useAppContext().currentWorkspace` -- full context
- `useSelector(ctx => ctx.currentWorkspace)` -- selector for minimal re-renders

Role-based access is derived as booleans:
- `isCurrentWorkspaceManager` = owner or admin
- `isCurrentWorkspaceOwner` = owner only
- `isCurrentWorkspaceEditor` = owner, admin, or editor
- `isCurrentWorkspaceDatasetOperator` = dataset_operator role

### 8.2 Workspace Switching

The `WorkspaceProvider` provides a list of all workspaces. Workspace switching
triggers re-fetching of workspace-scoped data. The API path convention
`/workspaces/current/...` means the backend determines the active workspace from
the session, not from a client-side parameter.

### 8.3 Tenant Scoping in API Calls

All API calls go through the centralized `service/base.ts` fetch wrapper which
automatically includes auth cookies. The backend resolves tenant from the session.
There is no client-side tenant ID in request headers.

---

## 9. Draft/Unsaved Changes Handling

### 9.1 Workflow Draft Sync

The `WorkflowDraftSlice` implements auto-save:

1. **Debounced sync**: A 5-second debounced function (`debouncedSyncWorkflowDraft`)
   batches rapid changes before syncing to the server.
2. **Hash-based change detection**: `syncWorkflowDraftHash` tracks the last synced
   state to avoid unnecessary API calls.
3. **Sync status indicator**: `isSyncingWorkflowDraft` drives a UI indicator.
4. **Flush on exit**: `flushPendingSync()` calls `debouncedFn.flush()` to force
   immediate sync (used on page unload via `syncWorkflowDraftWhenPageClose`).

### 9.2 Backup/Restore

- `backupDraft` stores a complete snapshot (nodes, edges, viewport, features, env vars)
- `handleBackupDraft` / `handleLoadBackupDraft` (in HooksStore) manage backup operations
- `handleRestoreFromPublishedWorkflow` reverts to the last published version

### 9.3 Version History

- `VersionSlice` tracks `draftUpdatedAt` and `publishedAt` timestamps
- `currentVersion` holds the selected version for comparison
- `isRestoring` flag prevents UI interaction during restore

### 9.4 Undo/Redo

- `WorkflowHistoryStore` uses `zundo` temporal middleware
- Records node and edge snapshots with `fast-deep-equal` deduplication
- Custom `setState` strips selection state before recording (to avoid undo toggling selection)

---

## 10. URL/Routing State

### 10.1 Next.js App Router

Dify uses the Next.js App Router with route groups:

- `(commonLayout)` -- authenticated pages (apps, datasets, plugins, tools, explore)
- `(shareLayout)` -- public web app pages (chat, workflow, completion embeds)
- Top-level routes: signin, signup, forgot-password, reset-password, install, init,
  activate, oauth-callback, education-apply

### 10.2 URL State with nuqs

The marketplace uses `nuqs` (Next.js URL state management) for search parameters:

- `useQueryState('q', ...)` -- search text
- `useQueryState('category', ...)` -- active plugin type filter
- `useQueryState('tags', ...)` -- tag filter

These are wrapped in custom hooks that conditionally use URL state or Jotai atoms
depending on a `preserveSearchStateInQueryAtom` flag. When the marketplace is embedded
in a modal, state stays in atoms; when on a full page, state syncs to URL params.

### 10.3 Route-Driven Data Loading

The web app store (`WebAppStoreProvider`) extracts `shareCode` from the URL pathname
and triggers access mode fetching. URL search params are also parsed for embedded
user/conversation IDs.

---

## 11. Performance Patterns

### 11.1 Selective Re-Renders

- **use-context-selector**: Both `AppContext` and `ProviderContext` use the
  `use-context-selector` library instead of standard React context. This allows
  consumers to subscribe to specific fields: `useSelector(ctx => ctx.currentWorkspace.role)`.
  Standard React context would re-render all consumers on any context value change.

- **Zustand selectors**: All context-scoped stores expose `useStore(selector)` that
  leverages Zustand's built-in shallow comparison. Components select only the fields
  they need.

- **subscribeWithSelector middleware**: `TriggerStatusStore` uses this for external
  subscriptions that react to specific state changes without React re-renders.

### 11.2 Memoization

- `useMemo` for derived values in context providers (role booleans, version info)
- `useCallback` for stable function references passed to children
- `useRef` for store instances in context-scoped providers (store created once,
  never recreated on re-render)

### 11.3 Debouncing

- Workflow draft sync debounced at 5 seconds
- Panel width persistence uses localStorage (read on init, written on change)

### 11.4 Immutable Updates

- `immer` (via `produce()`) used in `InspectVarsSlice` and `DatasetsDetailStore`
  for complex nested state updates
- All other stores use simple spread patterns (shallow state)

### 11.5 Code Splitting

- Next.js App Router provides route-based code splitting automatically
- The workflow store and its 13+ slices are only loaded when entering workflow pages
- Context-scoped stores are created lazily via `useRef` (first render only)
- TanStack DevTools loaded via dynamic import (`TanStackDevtoolsLoader`)
- `ReactScanLoader` loaded lazily for development profiling

### 11.6 localStorage Persistence

Several values persist across sessions via localStorage:
- `workflow-operation-mode` (pointer vs hand control)
- `workflow-node-panel-width`
- `debug-and-preview-panel-width`
- `workflow-variable-inpsect-panel-height`
- `workflow-canvas-maximize`
- `anthropic_quota_notice` (dismissal flag)
- Token refresh lock state (cross-tab coordination)

---

## 12. Jotai Usage (Marketplace Only)

Jotai atoms are used exclusively in the marketplace plugin browser:

- `marketplaceSortAtom` -- sort configuration
- `searchPluginTextAtom` -- search query text
- `activePluginTypeAtom` -- selected category filter
- `filterPluginTagsAtom` -- active tag filters
- `preserveSearchStateInQueryAtom` -- flag to switch between URL and atom storage
- `searchModeAtom` -- derived search mode flag

The dual-mode pattern (atom vs URL state) allows the same marketplace component to work
both as a standalone page (URL state for shareability) and as an embedded modal (atom
state for encapsulation).

---

## 13. Patterns Summary for Reimplementation

### Pattern 1: Context-Scoped Zustand Store

Used when multiple instances of a component tree need independent state (e.g.,
multiple workflow editors).

Architecture:
1. Define slices as `StateCreator` functions
2. Compose into a single store via `createStore()` with spread
3. Wrap in React Context
4. Provide via a provider component with `useRef` for stable reference
5. Access via `useStore(selector)` hook

### Pattern 2: Global Singleton Store

Used for app-wide UI state that has exactly one instance.

Architecture:
1. Call `create<Shape>(set => ({...}))` at module level
2. Import and call the hook directly in any component

### Pattern 3: Hybrid Query + Store

Used when server data needs both cache management and synchronous access.

Architecture:
1. TanStack Query fetches data
2. Query success handler writes into a Zustand store
3. Components read from either source depending on need

### Pattern 4: Callback Registry Store

Used to decouple action implementations from UI.

Architecture:
1. Store holds function references with `noop` defaults
2. Page-level component injects real implementations via `refreshAll()`
3. UI components call functions from the store without knowing the implementation

### Pattern 5: Temporal (Undo/Redo) Store

Used for history management in editors.

Architecture:
1. Zustand store with `zundo` `temporal` middleware
2. Deep equality check prevents duplicate history entries
3. Custom `setState` normalizes state before recording

---

## 14. Key Libraries

| Library | Version Context | Purpose |
|---------|----------------|---------|
| zustand | v4/v5 | Client state (primary) |
| @tanstack/react-query | v5 | Server state |
| jotai | minimal | Marketplace atoms |
| nuqs | v2 | URL search params |
| zundo | temporal middleware | Undo/redo history |
| immer | produce() | Immutable nested updates |
| use-context-selector | v2 | Fine-grained context subscriptions |
| ahooks | useEventEmitter | Cross-component events |
| es-toolkit | isEqual, debounce, noop | Utilities |
| fast-deep-equal | isDeepEqual | History equality checks |
| next-themes | ThemeProvider | Dark/light mode |
| js-cookie | Cookies.get() | CSRF token reading |

---

## 15. Anti-Patterns and Technical Debt

1. **Mixed state fetching in ProviderContext**: Billing data uses imperative
   `fetchCurrentPlanInfo()` with `useState` rather than React Query. This creates
   inconsistency with the rest of the data fetching layer.

2. **Mutex via state spreading**: The `ChatVariableSlice` and `EnvVariableSlice`
   implement mutual exclusion of panels by spreading `hideAllPanel` on show.
   This couples slices implicitly.

3. **Store callback pattern complexity**: The `HooksStore` callback registry has
   ~25 function slots. This works but makes it hard to trace which page provides
   which implementation.

4. **localStorage as persistence layer**: Panel dimensions and preferences use
   raw localStorage with string keys. No migration strategy if keys change.

5. **Recursive SSE retry**: `ssePost` calls itself on 401, which could theoretically
   infinite-loop if token refresh keeps failing (mitigated by the refresh timeout).
