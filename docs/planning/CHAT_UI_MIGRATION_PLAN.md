# Plan: Migrate to @assistant-ui/react for All Modules

## Objective

Replace ~1,927 lines of custom chat UI code with @assistant-ui/react to:
1. Eliminate maintenance burden (~540 lines deleted, ~400 lines added = net -140 lines)
2. Get production-hardened tool rendering, markdown, reasoning, auto-scroll
3. Enable easy chat rollout to Analysis, Decisions, Knowledge modules
4. Use declarative `makeAssistantToolUI` pattern for tool UIs

**App:** `~/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/`

**Backend:** No changes needed — existing `/api/v1/agent/chat` already outputs AI SDK Data Stream Protocol

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  NyqstAssistantProvider (new)                                   │
│    └── useVercelAIRuntime (from @assistant-ui/react-ai-sdk)     │
│          └── DefaultChatTransport (reuse existing pattern)      │
│                └── POST /api/v1/agent/chat (unchanged)          │
├─────────────────────────────────────────────────────────────────┤
│  ChatPanel (new reusable component)                             │
│    ├── ConversationSidebar (keep existing)                      │
│    ├── Thread (from @assistant-ui/react)                        │
│    │     ├── Messages with tool UIs (via makeAssistantToolUI)   │
│    │     └── Markdown, reasoning, auto-scroll (built-in)        │
│    ├── Composer (from @assistant-ui/react)                      │
│    └── SourcesSidebar (keep for Research module)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Install & Foundation

### 1.1 Install dependencies

```bash
cd ~/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/ui
npm install @assistant-ui/react @assistant-ui/react-ai-sdk
```

### 1.2 Configure Tailwind

**Modify:** `ui/tailwind.config.ts`
```typescript
// Add to content array:
content: [
  './src/**/*.{ts,tsx}',
  './node_modules/@assistant-ui/**/*.{js,ts,jsx,tsx}',
],
```

### 1.3 Import styles

**Modify:** `ui/src/index.css`
```css
@import "@assistant-ui/react/styles/tailwind-shadcn.css";
```

---

## Phase 2: Create Runtime Provider

**Create:** `ui/src/providers/assistant-runtime.tsx`

```typescript
import { useMemo, useCallback } from 'react';
import { useVercelAIRuntime } from '@assistant-ui/react-ai-sdk';
import { AssistantRuntimeProvider } from '@assistant-ui/react';
import { DefaultChatTransport } from 'ai';
import { useAuthStore } from '@/stores/auth-store';
import { useConversationStore } from '@/stores/conversation-store';

interface NyqstAssistantProviderProps {
  children: React.ReactNode;
  pointerId?: string;
  manifestSha256?: string;
  onConversationCreated?: (conversationId: string) => void;
}

export function NyqstAssistantProvider({
  children,
  pointerId,
  manifestSha256,
  onConversationCreated,
}: NyqstAssistantProviderProps) {
  const { token, tenantId } = useAuthStore();
  const { activeConversationId, activeSessionId, setActiveConversationId } = useConversationStore();

  const transport = useMemo(() => new DefaultChatTransport({
    api: '/api/v1/agent/chat',
    headers: () => ({
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': tenantId || '',
    }),
    prepareSendMessagesRequest({ messages, body }) {
      const converted = messages.map((msg) => ({
        role: msg.role,
        content: msg.parts
          .filter((p): p is { type: 'text'; text: string } => p.type === 'text')
          .map((p) => p.text)
          .join(''),
      }));
      return {
        body: {
          messages: converted,
          pointer_id: pointerId,
          manifest_sha256: manifestSha256,
          conversation_id: activeConversationId,
          session_id: activeSessionId,
          ...body,
        },
      };
    },
  }), [token, tenantId, pointerId, manifestSha256, activeConversationId, activeSessionId]);

  const handleFinish = useCallback(({ response }: { response: Response }) => {
    const conversationId = response.headers.get('X-Conversation-Id');
    if (conversationId && conversationId !== activeConversationId) {
      setActiveConversationId(conversationId);
      onConversationCreated?.(conversationId);
    }
  }, [activeConversationId, setActiveConversationId, onConversationCreated]);

  const runtime = useVercelAIRuntime({
    transport,
    maxSteps: 10,
    onFinish: handleFinish,
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}
```

---

## Phase 3: Create Tool UIs

**Create:** `ui/src/components/chat/tool-uis.tsx`

```typescript
import { makeAssistantToolUI } from '@assistant-ui/react';
import { CheckCircle2, Loader2, XCircle } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useState } from 'react';

// Generic tool UI for all tools (fallback)
export const GenericToolUI = makeAssistantToolUI({
  toolName: '*',
  render: ({ toolName, args, result, status }) => {
    const [isOpen, setIsOpen] = useState(false);
    const isLoading = status.type === 'running';
    const isError = status.type === 'incomplete' && status.reason === 'error';
    const isComplete = status.type === 'complete';

    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="my-2 rounded-lg border bg-muted/50 p-2">
          <CollapsibleTrigger className="flex w-full items-center gap-2 text-sm">
            {isComplete && <CheckCircle2 className="h-4 w-4 text-green-500" />}
            {isError && <XCircle className="h-4 w-4 text-destructive" />}
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            <span className="font-mono text-xs truncate">{toolName}</span>
            <span className="text-[10px] text-muted-foreground ml-auto">
              {isComplete ? 'completed' : isError ? 'failed' : 'running...'}
            </span>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="mt-2 space-y-2 pl-6">
              {args && (
                <div>
                  <span className="text-[10px] font-medium uppercase text-muted-foreground">Input</span>
                  <pre className="mt-1 overflow-auto rounded bg-background p-2 text-xs max-h-32">
                    {JSON.stringify(args, null, 2)}
                  </pre>
                </div>
              )}
              {isComplete && result && (
                <div>
                  <span className="text-[10px] font-medium uppercase text-muted-foreground">Output</span>
                  {typeof result === 'string' ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none mt-1">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
                    </div>
                  ) : (
                    <pre className="mt-1 overflow-auto rounded bg-background p-2 text-xs max-h-48">
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          </CollapsibleContent>
        </div>
      </Collapsible>
    );
  },
});

// Search documents tool - shows document results nicely
export const SearchDocumentsToolUI = makeAssistantToolUI({
  toolName: 'search_documents',
  render: ({ args, result, status }) => {
    const isComplete = status.type === 'complete';
    const query = args?.query as string | undefined;

    return (
      <div className="my-2 rounded-lg border bg-blue-50 dark:bg-blue-950/30 p-3">
        <div className="flex items-center gap-2 text-sm">
          {isComplete ? (
            <CheckCircle2 className="h-4 w-4 text-blue-500" />
          ) : (
            <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
          )}
          <span className="font-medium">Searching documents</span>
          {query && <span className="text-muted-foreground">for "{query}"</span>}
        </div>
        {isComplete && result && (
          <div className="mt-2 text-xs text-muted-foreground">
            Found relevant passages
          </div>
        )}
      </div>
    );
  },
});
```

---

## Phase 4: Create Thread Sync Hook

**Create:** `ui/src/hooks/use-thread-sync.ts`

```typescript
import { useEffect } from 'react';
import { useAssistantRuntime } from '@assistant-ui/react';
import { conversationsApi } from '@/api/conversations';
import { useConversationStore } from '@/stores/conversation-store';

export function useThreadSync() {
  const runtime = useAssistantRuntime();
  const { activeConversationId } = useConversationStore();

  useEffect(() => {
    if (!activeConversationId) {
      // New conversation - clear messages
      runtime.thread.import({ messages: [] });
      return;
    }

    async function loadMessages() {
      try {
        const result = await conversationsApi.getMessages(activeConversationId);
        const messages = result.items.map((msg) => ({
          id: msg.id,
          role: msg.role as 'user' | 'assistant',
          content: [{ type: 'text' as const, text: msg.content || '' }],
          createdAt: new Date(msg.created_at),
        }));
        runtime.thread.import({ messages });
      } catch (error) {
        console.error('Failed to load messages:', error);
      }
    }

    loadMessages();
  }, [activeConversationId, runtime]);
}
```

---

## Phase 5: Create Reusable ChatPanel

**Create:** `ui/src/components/chat/ChatPanel.tsx`

```typescript
import { Thread, Composer, ThreadWelcome } from '@assistant-ui/react';
import { NyqstAssistantProvider } from '@/providers/assistant-runtime';
import { ConversationSidebar } from './conversation-sidebar';
import { GenericToolUI, SearchDocumentsToolUI } from './tool-uis';
import { useThreadSync } from '@/hooks/use-thread-sync';
import { cn } from '@/lib/utils';

interface ChatPanelProps {
  module: 'research' | 'analysis' | 'decisions' | 'knowledge';
  scopeContext?: {
    pointerId?: string;
    manifestSha256?: string;
  };
  welcomeTitle?: string;
  welcomeMessage?: string;
  suggestions?: string[];
  showSidebar?: boolean;
  rightPanel?: React.ReactNode;
  className?: string;
}

function ChatPanelInner({
  welcomeTitle,
  welcomeMessage,
  suggestions,
  showSidebar = true,
  rightPanel,
  className,
}: Omit<ChatPanelProps, 'module' | 'scopeContext'>) {
  useThreadSync();

  return (
    <div className={cn('flex h-full', className)}>
      {showSidebar && <ConversationSidebar className="w-64 shrink-0 border-r" />}

      <div className="flex flex-1 flex-col min-w-0">
        <Thread
          className="flex-1"
          welcome={
            <ThreadWelcome>
              <ThreadWelcome.Avatar />
              {welcomeTitle && (
                <h1 className="text-xl font-semibold">{welcomeTitle}</h1>
              )}
              {welcomeMessage && (
                <p className="text-muted-foreground">{welcomeMessage}</p>
              )}
              {suggestions && suggestions.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {suggestions.map((s) => (
                    <ThreadWelcome.Suggestion key={s} suggestion={{ prompt: s }}>
                      {s}
                    </ThreadWelcome.Suggestion>
                  ))}
                </div>
              )}
            </ThreadWelcome>
          }
        />
        <div className="border-t p-4">
          <Composer placeholder="Ask a question..." />
        </div>
      </div>

      {rightPanel && (
        <div className="w-80 shrink-0 border-l overflow-auto">
          {rightPanel}
        </div>
      )}
    </div>
  );
}

export function ChatPanel({ module, scopeContext, ...props }: ChatPanelProps) {
  return (
    <NyqstAssistantProvider
      pointerId={scopeContext?.pointerId}
      manifestSha256={scopeContext?.manifestSha256}
    >
      <GenericToolUI />
      <SearchDocumentsToolUI />
      <ChatPanelInner {...props} />
    </NyqstAssistantProvider>
  );
}
```

---

## Phase 6: Migrate ResearchPage

**Modify:** `ui/src/pages/ResearchPage.tsx`

Replace the current 567-line implementation with a simplified version using ChatPanel:

```typescript
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { SourcesSidebar } from '@/components/chat/SourcesSidebar';
import { NotebookSelector } from '@/components/NotebookSelector';
import { useSessionLifecycle } from '@/hooks/use-session-lifecycle';
import { pointersApi } from '@/api/pointers';

export function ResearchPage() {
  const [selectedPointerId, setSelectedPointerId] = useState<string | null>(null);
  const [sources, setSources] = useState<AgentSource[]>([]);

  // Session lifecycle (create on mount, idle on unmount)
  useSessionLifecycle('research');

  // Load pointer details for manifest_sha256
  const { data: pointer } = useQuery({
    queryKey: ['pointer', selectedPointerId],
    queryFn: () => pointersApi.get(selectedPointerId!),
    enabled: !!selectedPointerId,
  });

  return (
    <div className="flex h-full flex-col">
      <div className="border-b p-4">
        <NotebookSelector
          value={selectedPointerId}
          onChange={setSelectedPointerId}
        />
      </div>

      {selectedPointerId && pointer ? (
        <ChatPanel
          module="research"
          scopeContext={{
            pointerId: selectedPointerId,
            manifestSha256: pointer.manifest_sha256,
          }}
          welcomeTitle="Research Assistant"
          welcomeMessage="Ask questions about your documents"
          suggestions={[
            'What are the key terms?',
            'Summarize the main points',
            'What are the risk factors?',
          ]}
          rightPanel={<SourcesSidebar sources={sources} />}
        />
      ) : (
        <div className="flex flex-1 items-center justify-center text-muted-foreground">
          Select a notebook to start
        </div>
      )}
    </div>
  );
}
```

This reduces ResearchPage from ~567 lines to ~60 lines.

---

## Phase 7: Extract Session Lifecycle Hook

**Create:** `ui/src/hooks/use-session-lifecycle.ts`

```typescript
import { useEffect, useRef } from 'react';
import { useConversationStore } from '@/stores/conversation-store';
import { sessionsApi } from '@/api/sessions';

export function useSessionLifecycle(module: string) {
  const { setActiveSessionId, activeSessionId } = useConversationStore();
  const sessionRef = useRef<string | null>(null);

  // Create session on mount
  useEffect(() => {
    async function createSession() {
      const session = await sessionsApi.create({ module });
      setActiveSessionId(session.id);
      sessionRef.current = session.id;
    }
    createSession();

    // Idle session on unmount
    return () => {
      if (sessionRef.current) {
        sessionsApi.transition(sessionRef.current, 'idle').catch(console.error);
      }
    };
  }, [module, setActiveSessionId]);

  return activeSessionId;
}
```

---

## Phase 8: Create SourcesSidebar Component

**Create:** `ui/src/components/chat/SourcesSidebar.tsx`

Extract the sources display from current ResearchPage:

```typescript
import { FileText, ExternalLink } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface AgentSource {
  artifact_sha256: string;
  filename: string;
  chunk_id: string;
  score: number;
  content_preview?: string;
}

interface SourcesSidebarProps {
  sources: AgentSource[];
}

export function SourcesSidebar({ sources }: SourcesSidebarProps) {
  if (sources.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground">
        Sources will appear here when the assistant cites documents
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <h3 className="font-medium text-sm">Sources</h3>
      {sources.map((source, i) => (
        <div
          key={`${source.artifact_sha256}-${source.chunk_id}`}
          className="rounded-lg border p-3 text-sm"
        >
          <div className="flex items-start gap-2">
            <FileText className="h-4 w-4 mt-0.5 text-muted-foreground" />
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{source.filename}</p>
              {source.content_preview && (
                <p className="mt-1 text-xs text-muted-foreground line-clamp-3">
                  {source.content_preview}
                </p>
              )}
            </div>
            <Badge variant="secondary" className="text-[10px]">
              {Math.round(source.score * 100)}%
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## Phase 9: Cleanup

### Delete these files (540 lines removed):
- `ui/src/hooks/use-agent-chat.ts` (266 lines) — replaced by runtime
- `ui/src/components/chat/message-content.tsx` (71 lines) — built into Thread
- `ui/src/components/chat/tool-call-card.tsx` (107 lines) — replaced by tool-uis
- `ui/src/components/chat/reasoning-block.tsx` (38 lines) — built into Thread

### Keep these files unchanged:
- `ui/src/components/chat/conversation-sidebar.tsx` — still needed
- `ui/src/components/chat/message-feedback.tsx` — still needed
- `ui/src/components/chat/branch-indicator.tsx` — still needed
- `ui/src/stores/conversation-store.ts` — still needed
- `ui/src/api/conversations.ts` — still needed

### Update tests:
- `ui/src/pages/__tests__/ResearchPage.test.tsx` — update selectors for Thread component
- `ui/src/components/chat/tool-call-card.test.tsx` — replace with tool-uis.test.tsx

---

## Files Summary

### Create (7 files, ~400 lines)
| File | Lines | Purpose |
|------|-------|---------|
| `ui/src/providers/assistant-runtime.tsx` | ~80 | Runtime provider with backend transport |
| `ui/src/components/chat/ChatPanel.tsx` | ~80 | Reusable chat panel component |
| `ui/src/components/chat/tool-uis.tsx` | ~100 | Tool UI registrations |
| `ui/src/components/chat/SourcesSidebar.tsx` | ~50 | Sources display (extracted) |
| `ui/src/hooks/use-thread-sync.ts` | ~40 | Conversation sync hook |
| `ui/src/hooks/use-session-lifecycle.ts` | ~30 | Session management hook |
| `ui/src/components/chat/tool-uis.test.tsx` | ~60 | Tool UI tests |

### Delete (4 files, ~540 lines)
| File | Lines | Reason |
|------|-------|--------|
| `ui/src/hooks/use-agent-chat.ts` | 266 | Replaced by runtime |
| `ui/src/components/chat/message-content.tsx` | 71 | Built into Thread |
| `ui/src/components/chat/tool-call-card.tsx` | 107 | Replaced by tool-uis |
| `ui/src/components/chat/reasoning-block.tsx` | 38 | Built into Thread |

### Modify (4 files)
| File | Change |
|------|--------|
| `ui/package.json` | Add @assistant-ui/react, @assistant-ui/react-ai-sdk |
| `ui/tailwind.config.ts` | Add assistant-ui content paths |
| `ui/src/index.css` | Import assistant-ui styles |
| `ui/src/pages/ResearchPage.tsx` | Simplify to ~60 lines using ChatPanel |

### Net Change: -140 lines (540 deleted - 400 added)

---

## Verification

After implementation, verify:

1. **Streaming works**: Send message → see token-by-token response
2. **Tool calls render**: Ask "What notebooks do I have?" → see tool card → see result
3. **Markdown renders**: Bold, lists, code blocks display correctly
4. **Conversation persistence**: Refresh page → messages reload
5. **New conversation**: Click "New" → empty thread → send message → conversation created
6. **Conversation switching**: Click sidebar item → messages load
7. **Sources display**: Ask about documents → sources appear in right panel
8. **Session lifecycle**: Navigate away → session transitions to idle

**Test commands:**
```bash
cd ~/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/ui
npm run test
npm run dev  # Manual browser verification
```

---

## Future: Add Chat to Other Modules

Once ResearchPage works, adding chat to other modules is trivial:

**AnalysisPage:**
```typescript
<ChatPanel
  module="analysis"
  welcomeTitle="Analysis Assistant"
  welcomeMessage="Build structured analysis from your documents"
  suggestions={['Extract entities', 'Create comparison table', 'Identify relationships']}
/>
```

**DecisionsPage:**
```typescript
<ChatPanel
  module="decisions"
  welcomeTitle="Decision Assistant"
  welcomeMessage="Document decisions with evidence and confidence"
  suggestions={['Create new decision', 'Review pending items', 'Show audit trail']}
/>
```

Each module just needs its own backend graph in `src/intelli/agents/graphs/` — the frontend is ready.
