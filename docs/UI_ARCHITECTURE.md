# UI Architecture — Agent-First Document Intelligence Platform

## Overview

The UI is an **agent-first workbench** — a multi-pane IDE-like interface where users can observe, guide, and review agentic work. It's not a traditional form-based app; it's designed around:

1. **Observability**: See what agents are doing in real-time (runs, tool calls, artifacts)
2. **Context pinning**: Pin bundles/corpora/artifacts to provide agent context
3. **Review and approval**: Approve promotions, review outputs, add comments
4. **Navigation**: URI-based addressing for all resources

---

## 1. Technology Stack

### Frontend
- **React 18+** with TypeScript
- **Vite** for build tooling (fast HMR, ESBuild)
- **shadcn/ui** + Radix UI for accessible components
- **Tailwind CSS** for styling
- **TanStack Query** (React Query) for server state
- **Zustand** for client state (workbench layout, pinned context)
- **react-resizable-panels** for IDE-like pane splitting

### Real-time
- **Server-Sent Events (SSE)** for run events, artifact updates
- HTTP long-polling fallback

### Routing
- **TanStack Router** or React Router for URI-based navigation

---

## 2. Resource URI Scheme

All resources are addressable via URIs:

```
project://{project_id}
bundle://{namespace}/{name}
corpus://{namespace}/{name}
manifest://{sha256}
artifact://{sha256}
run://{run_id}
run://{run_id}/events
pointer://{pointer_id}
kb://{kb_id}
claim://{claim_id}
```

These URIs drive:
- Navigation (address bar, deep links)
- Pane content (each pane renders a resource URI)
- Context pinning (pinned resources are URIs)

---

## 3. Workbench Layout

### 3.1 Shell Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ Top Bar: Search │ Context Breadcrumb │ User │ Settings          │
├───────┬─────────────────────────────────────────────────┬───────┤
│       │                                                 │       │
│ Side  │                 Main Work Area                  │ Right │
│ Panel │              (Resizable Panes)                  │ Panel │
│       │                                                 │       │
│ Nav   │  ┌─────────────────┬───────────────────────┐   │Context│
│ Tree  │  │                 │                       │   │Pinboard
│       │  │  Primary Pane   │   Secondary Pane      │   │       │
│       │  │  (Run Explorer) │   (Artifact Viewer)   │   │       │
│       │  │                 │                       │   │       │
│       │  └─────────────────┴───────────────────────┘   │       │
│       │  ┌─────────────────────────────────────────┐   │       │
│       │  │            Bottom Pane                  │   │       │
│       │  │        (Chat / Terminal / Logs)         │   │       │
│       │  └─────────────────────────────────────────┘   │       │
├───────┴─────────────────────────────────────────────────┴───────┤
│ Status Bar: Active Run │ Token Usage │ Connection Status        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Pane Types

| Pane Type | Description | Dynamic Content |
|-----------|-------------|-----------------|
| **RunExplorer** | Timeline + DAG of run steps/events | SSE stream of events |
| **ArtifactBrowser** | List/search artifacts by type, project | On-demand loading |
| **ManifestViewer** | Tree view of manifest entries | Static once loaded |
| **DocumentViewer** | PDF/DocIR viewer with evidence highlights | Static + overlays |
| **TableViewer** | Parquet/JSON table data | Pagination |
| **DiffViewer** | Side-by-side manifest/artifact diff | Computed on demand |
| **Chat** | Thread with agent interaction | SSE for responses |
| **Planner** | Plan artifact with step status | Updated from run events |
| **PointerHistory** | Timeline of pointer changes | On-demand |
| **ApprovalPanel** | Pending approvals for corpus promotion | WebSocket/SSE |

---

## 4. State Management

### 4.1 Server State (TanStack Query)

All API data is managed via React Query:

```typescript
// Queries (read)
useArtifact(sha256)
useManifest(sha256)
usePointer(namespace, name)
useRun(runId)
useRunEvents(runId, options)
usePointers(namespace, filters)
useManifestHistory(sha256)

// Mutations (write)
useUploadArtifact()
useCreateManifest()
useAdvancePointer()
useCreateRun()
useStartRun()
useCompleteRun()
```

### 4.2 Client State (Zustand)

```typescript
interface WorkbenchState {
  // Layout
  layout: PaneLayout;
  setLayout: (layout: PaneLayout) => void;

  // Pinned context
  pinnedResources: ResourceUri[];
  pinResource: (uri: ResourceUri) => void;
  unpinResource: (uri: ResourceUri) => void;

  // Active resource
  activeResource: ResourceUri | null;
  setActiveResource: (uri: ResourceUri) => void;

  // Workspace (saved configurations)
  savedWorkspaces: Workspace[];
  loadWorkspace: (id: string) => void;
}
```

### 4.3 Real-time State (SSE)

```typescript
// Hook for subscribing to run events
function useRunEventStream(runId: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const eventSource = new EventSource(`/api/v1/runs/${runId}/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Update React Query cache incrementally
      queryClient.setQueryData(['run-events', runId], (old) => [...old, data]);
    };

    return () => eventSource.close();
  }, [runId]);
}
```

---

## 5. Key Components

### 5.1 Shell Components

```
components/
├── shell/
│   ├── Workbench.tsx          # Main layout container
│   ├── TopBar.tsx             # Search, breadcrumb, user menu
│   ├── SideNav.tsx            # Navigation tree
│   ├── ContextPinboard.tsx    # Right panel with pinned resources
│   ├── StatusBar.tsx          # Bottom status
│   └── PaneContainer.tsx      # Resizable pane wrapper
```

### 5.2 Viewer Components

```
components/
├── viewers/
│   ├── RunExplorer/
│   │   ├── RunTimeline.tsx    # Chronological event list
│   │   ├── RunDAG.tsx         # DAG visualization
│   │   ├── EventCard.tsx      # Single event display
│   │   └── StepDetails.tsx    # Expanded step view
│   ├── ArtifactBrowser/
│   │   ├── ArtifactList.tsx   # Filterable list
│   │   ├── ArtifactCard.tsx   # Preview card
│   │   └── ArtifactFilters.tsx
│   ├── ManifestViewer/
│   │   ├── ManifestTree.tsx   # Entry tree
│   │   ├── EntryDetails.tsx
│   │   └── ManifestMeta.tsx
│   ├── DocumentViewer/
│   │   ├── PDFViewer.tsx      # PDF rendering
│   │   ├── EvidenceOverlay.tsx # Highlight evidence spans
│   │   └── CitationSidebar.tsx
│   ├── TableViewer/
│   │   ├── DataTable.tsx      # Virtualized table
│   │   └── ColumnConfig.tsx
│   ├── DiffViewer/
│   │   ├── ManifestDiff.tsx   # Side-by-side manifest diff
│   │   └── ArtifactDiff.tsx
│   └── Chat/
│       ├── ThreadView.tsx     # Message list
│       ├── MessageInput.tsx
│       └── MessageCard.tsx
```

### 5.3 Common Components

```
components/
├── common/
│   ├── ResourceLink.tsx       # Clickable resource URI
│   ├── SHA256Badge.tsx        # Truncated hash with copy
│   ├── TimestampDisplay.tsx   # Relative/absolute time
│   ├── StatusBadge.tsx        # Run/step status
│   ├── LoadingState.tsx
│   └── ErrorBoundary.tsx
```

---

## 6. API Client

### 6.1 Generated Types

Use OpenAPI spec to generate TypeScript types:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/types.ts
```

### 6.2 API Client Structure

```typescript
// src/api/client.ts
const api = {
  artifacts: {
    upload: (file: File) => fetch('/api/v1/artifacts', { method: 'POST', body: formData }),
    get: (sha256: string) => fetch(`/api/v1/artifacts/${sha256}`),
    getUrl: (sha256: string) => fetch(`/api/v1/artifacts/${sha256}/url`),
  },
  manifests: {
    create: (data: ManifestCreate) => fetch('/api/v1/manifests', { method: 'POST', body }),
    get: (sha256: string) => fetch(`/api/v1/manifests/${sha256}`),
    diff: (old: string, new: string) => fetch(`/api/v1/manifests/${old}/diff/${new}`),
  },
  pointers: {
    resolve: (ns: string, name: string) => fetch(`/api/v1/pointers/${ns}/${name}/resolve`),
    advance: (id: string, data: PointerAdvance) => fetch(`/api/v1/pointers/${id}/advance`, { method: 'PUT', body }),
  },
  runs: {
    create: (data: RunCreate) => fetch('/api/v1/runs', { method: 'POST', body }),
    get: (id: string) => fetch(`/api/v1/runs/${id}`),
    events: (id: string) => fetch(`/api/v1/runs/${id}/events`),
    stream: (id: string) => new EventSource(`/api/v1/runs/${id}/stream`), // SSE
  },
};
```

---

## 7. Backend SSE Endpoints (to add)

### 7.1 Run Event Stream

```python
# GET /api/v1/runs/{run_id}/stream
@router.get("/{run_id}/stream")
async def stream_run_events(
    run_id: UUID,
    service: LedgerServiceDep,
) -> StreamingResponse:
    """SSE stream of run events for real-time UI updates."""

    async def event_generator():
        last_sequence = 0
        while True:
            events = await service.get_events(
                run_id=run_id,
                since_sequence=last_sequence,
                limit=100,
            )
            for event in events:
                yield f"data: {event.model_dump_json()}\n\n"
                last_sequence = event.sequence_num
            await asyncio.sleep(0.5)  # Poll interval

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

### 7.2 Global Activity Stream

```python
# GET /api/v1/activity/stream
# Streams: new artifacts, pointer moves, run status changes
```

---

## 8. What Needs to be Dynamic

| Feature | Update Mechanism | Frequency |
|---------|------------------|-----------|
| Run events (steps, tool calls) | SSE | Real-time |
| Run status changes | SSE | On change |
| Artifact uploads (by others) | SSE / Polling | Low freq |
| Pointer advances | SSE | On change |
| Approval requests | SSE | On change |
| Chat messages | SSE | Real-time |
| Token usage counters | SSE | Per run event |

---

## 9. What Needs to be Wired

### 9.1 Core Flows

1. **Upload Document → Parse → Create Manifest → Advance Pointer**
   - Upload UI → API → triggers parse run → run events stream → manifest created → pointer advanced
   - UI shows progress via run explorer

2. **Research Session**
   - User pins context (corpus/bundle)
   - Agent runs with pinned context
   - Events stream to UI
   - Outputs published → manifest → pointer

3. **Corpus Promotion**
   - User requests promotion (bundle → corpus)
   - Evaluation gates run (shown in UI)
   - Approval panel appears
   - Human approves → pointer moved

### 9.2 Wiring Checklist

- [ ] API client with all endpoints
- [ ] SSE subscription hooks
- [ ] React Query queries for all resources
- [ ] Zustand store for workbench state
- [ ] Pane routing (URI → component)
- [ ] Context pinning (add to agent calls)
- [ ] Upload flow with progress
- [ ] Run creation and monitoring
- [ ] Manifest browsing and diff
- [ ] Pointer management UI

---

## 10. Implementation Priority

### Phase 1: Minimal Viable Workbench
1. Workbench shell with resizable panes
2. Artifact upload + browser
3. Run creation + event stream viewer
4. Manifest viewer

### Phase 2: Full Workflow Support
1. Document viewer with DocIR
2. Diff viewer
3. Pointer management + history
4. Chat/thread integration

### Phase 3: Governance + Collaboration
1. Approval panels
2. Context pinboard
3. Workspace save/load
4. Multi-user presence

---

## 11. File Structure

```
web/
├── public/
├── src/
│   ├── api/
│   │   ├── client.ts          # API functions
│   │   ├── types.ts           # Generated from OpenAPI
│   │   └── hooks.ts           # React Query hooks
│   ├── components/
│   │   ├── shell/             # Workbench layout
│   │   ├── viewers/           # Content viewers
│   │   └── common/            # Shared components
│   ├── stores/
│   │   └── workbench.ts       # Zustand store
│   ├── hooks/
│   │   ├── useEventStream.ts  # SSE subscription
│   │   └── useResourceUri.ts  # URI parsing
│   ├── lib/
│   │   └── utils.ts           # Utilities
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```
