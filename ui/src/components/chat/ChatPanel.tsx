/**
 * Reusable chat panel component using @assistant-ui/react-ui.
 *
 * Composes Thread, Composer, and conversation sidebar into a complete
 * chat experience. Can be used in Research, Analysis, Decisions, and
 * Knowledge modules with different welcome messages and suggestions.
 */

import { useEffect, useCallback, useState } from 'react'
import { Thread, Composer, ThreadConfigProvider } from '@assistant-ui/react-ui'
import { useQuery } from '@tanstack/react-query'
import { Activity, X } from 'lucide-react'

import { NyqstAssistantProvider, type ScopeContext } from '@/providers/assistant-runtime'
import { ConversationSidebar } from '@/components/chat/conversation-sidebar'
import { GenericToolUI, SearchDocumentsToolUI } from '@/components/chat/tool-uis'
import { MessageMetadataFooter } from '@/components/chat/message-metadata'
import { CitationAwareText } from '@/components/chat/CitationAwareText'
import { RunTimeline } from '@/components/runs/RunTimeline'
import { useConversationStore } from '@/stores/conversation-store'
import { useRunStore } from '@/stores/run-store'
import { conversationsApi } from '@/api/conversations'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { SourcesProvider } from '@/contexts/SourcesContext'

interface ChatPanelProps {
  module: 'research' | 'analysis' | 'decisions' | 'knowledge'
  scopeContext?: ScopeContext
  welcomeTitle?: string
  welcomeMessage?: string
  suggestions?: string[]
  showSidebar?: boolean
  rightPanel?: React.ReactNode
  className?: string
}

interface ChatPanelInnerProps extends Omit<ChatPanelProps, 'module'> {
  scopeId?: string
}

function ChatPanelInner({
  welcomeTitle = 'Assistant',
  welcomeMessage,
  suggestions = [],
  showSidebar = true,
  rightPanel,
  className,
  scopeId,
}: Omit<ChatPanelInnerProps, 'module' | 'scopeContext'> & { scopeId?: string }) {
  const [showTimeline, setShowTimeline] = useState(false)
  const {
    conversations,
    activeConversationId,
    setConversations,
    updateConversation,
    removeConversation,
    setActiveConversationId,
  } = useConversationStore()
  const { activeRunId } = useRunStore()

  console.log('[ChatPanel] Current activeRunId:', activeRunId)

  // Fetch conversations - filtered by scope_id (pointer) if provided
  const conversationsQuery = useQuery({
    queryKey: ['conversations', scopeId],
    queryFn: () =>
      conversationsApi.list({
        limit: 50,
        ...(scopeId ? { scope_type: 'pointer', scope_id: scopeId } : {}),
      }),
  })

  useEffect(() => {
    if (conversationsQuery.data) {
      setConversations(conversationsQuery.data.items)
    }
  }, [conversationsQuery.data, setConversations])

  const handleNewConversation = useCallback(() => {
    setActiveConversationId(null)
  }, [setActiveConversationId])

  const handleSelectConversation = useCallback(
    (id: string) => {
      setActiveConversationId(id)
    },
    [setActiveConversationId]
  )

  const handleUpdateConversation = useCallback(
    (id: string, updates: Record<string, unknown>) => {
      updateConversation(id, updates)
    },
    [updateConversation]
  )

  const handleDeleteConversation = useCallback(
    (id: string) => {
      removeConversation(id)
      if (activeConversationId === id) {
        setActiveConversationId(null)
      }
    },
    [removeConversation, activeConversationId, setActiveConversationId]
  )

  return (
    <SourcesProvider>
      <ThreadConfigProvider
        config={{
          welcome: {
            message: welcomeTitle,
            suggestions: suggestions.map((prompt) => ({ prompt })),
          },
          strings: {
            composer: {
              input: {
                placeholder: 'Ask a question...',
              },
            },
            welcome: {
              message: welcomeMessage,
            },
          },
          assistantMessage: {
            allowCopy: true,
            allowReload: true,
            components: {
              Footer: MessageMetadataFooter,
              Text: CitationAwareText,
            },
          },
          tools: [GenericToolUI, SearchDocumentsToolUI],
        }}
      >
      <div className={cn('flex h-full', className)}>
        {showSidebar && (
          <ConversationSidebar
            conversations={conversations}
            activeId={activeConversationId}
            onSelect={handleSelectConversation}
            onCreate={handleNewConversation}
            onUpdate={handleUpdateConversation}
            onDelete={handleDeleteConversation}
          />
        )}

        <div className="flex flex-1 flex-col min-w-0">
          {/* Header with timeline toggle */}
          <div className="flex items-center justify-end gap-2 px-4 py-2 border-b">
            <Button
              variant={showTimeline ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setShowTimeline(!showTimeline)}
              disabled={!activeRunId}
              className="gap-2"
            >
              <Activity className="h-4 w-4" />
              <span className="sr-only sm:not-sr-only">Timeline</span>
            </Button>
          </div>

          <div className="flex-1 overflow-hidden">
            <Thread />
          </div>
          <div className="border-t p-4">
            <Composer />
          </div>
        </div>

        {/* Timeline panel */}
        {showTimeline && activeRunId && (
          <div className="w-80 shrink-0 border-l overflow-auto bg-muted/30">
            <div className="flex items-center justify-between px-4 py-2 border-b">
              <h3 className="text-sm font-medium">Run Timeline</h3>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => setShowTimeline(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <RunTimeline runId={activeRunId} />
          </div>
        )}

        {rightPanel && !showTimeline && (
          <div className="w-80 shrink-0 border-l overflow-auto bg-muted/30">{rightPanel}</div>
        )}
      </div>
    </ThreadConfigProvider>
    </SourcesProvider>
  )
}

export function ChatPanel({ module, scopeContext, ...props }: ChatPanelProps) {
  return (
    <NyqstAssistantProvider module={module} scopeContext={scopeContext}>
      <ChatPanelInner {...props} scopeId={scopeContext?.pointerId} />
    </NyqstAssistantProvider>
  )
}
