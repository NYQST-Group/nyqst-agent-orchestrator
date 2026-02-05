/**
 * Assistant runtime provider using @assistant-ui/react.
 *
 * Wraps useChatRuntime with the existing backend transport pattern
 * and handles conversation ID capture from response metadata.
 * Includes feedback adapter for thumbs up/down on assistant messages.
 */

import { useMemo, useCallback, useRef } from 'react'
import { useChatRuntime } from '@assistant-ui/react-ai-sdk'
import { AssistantRuntimeProvider } from '@assistant-ui/react'
import type { FeedbackAdapter } from '@assistant-ui/react'
import { DefaultChatTransport } from 'ai'
import { useQueryClient } from '@tanstack/react-query'

import { getAuthHeaders } from '@/stores/auth-store'
import { useConversationStore } from '@/stores/conversation-store'
import { useRunStore } from '@/stores/run-store'
import { conversationsApi } from '@/api/conversations'

/**
 * Scope context for document-scoped conversations.
 * Both fields must be provided together or neither.
 */
export interface ScopeContext {
  pointerId: string
  manifestSha256: string
}

/**
 * Message metadata from backend SSE stream.
 */
interface AssistantMessageMetadata {
  conversationId?: string
  runId?: string
  userMessageId?: string
  assistantMessageId?: string
  outputTokens?: number
  inputTokens?: number
  latencyMs?: number
}

/**
 * Type guard for messages with metadata.
 */
function hasMetadata(
  message: unknown
): message is { metadata: AssistantMessageMetadata } {
  if (typeof message !== 'object' || message === null) return false
  if (!('metadata' in message)) return false
  const meta = (message as Record<string, unknown>).metadata
  // typeof null === 'object' in JS, so must explicitly check
  return typeof meta === 'object' && meta !== null
}

interface NyqstAssistantProviderProps {
  children: React.ReactNode
  module: 'research' | 'analysis' | 'decisions' | 'knowledge'
  scopeContext?: ScopeContext
  onConversationCreated?: (conversationId: string) => void
}

export function NyqstAssistantProvider({
  children,
  module,
  scopeContext,
  onConversationCreated,
}: NyqstAssistantProviderProps) {
  const { activeConversationId, activeSessionId, setActiveConversationId, addConversation } =
    useConversationStore()
  const { setActiveRunId } = useRunStore()
  const queryClient = useQueryClient()

  // Track message ID mappings: assistant-ui internal ID -> backend UUID
  // We use a ref because we need to update it synchronously during stream processing
  // and access it in the feedback adapter without triggering re-renders
  const messageIdMapRef = useRef<Map<string, { conversationId: string; messageId: string }>>(
    new Map()
  )

  // Refs to capture current values in callbacks without causing transport recreation
  const moduleRef = useMemo(() => ({ current: module }), [])
  moduleRef.current = module
  const pointerIdRef = useMemo(() => ({ current: scopeContext?.pointerId }), [])
  pointerIdRef.current = scopeContext?.pointerId
  const manifestRef = useMemo(() => ({ current: scopeContext?.manifestSha256 }), [])
  manifestRef.current = scopeContext?.manifestSha256
  const conversationIdRef = useMemo(() => ({ current: activeConversationId }), [])
  conversationIdRef.current = activeConversationId
  const sessionIdRef = useMemo(() => ({ current: activeSessionId }), [])
  sessionIdRef.current = activeSessionId

  // Create a custom transport that includes our context in requests
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: '/api/v1/agent/chat',
        headers: () => getAuthHeaders(),
        prepareSendMessagesRequest({ messages, body }) {
          const converted = messages.map((msg) => ({
            role: msg.role,
            content: msg.parts
              .filter((p): p is { type: 'text'; text: string } => p.type === 'text')
              .map((p) => p.text)
              .join(''),
          }))
          return {
            body: {
              messages: converted,
              module: moduleRef.current,
              pointer_id: pointerIdRef.current,
              manifest_sha256: manifestRef.current,
              conversation_id: conversationIdRef.current,
              session_id: sessionIdRef.current,
              ...body,
            },
          }
        },
      }),
    // Transport is created once and uses refs for dynamic values
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )

  const handleFinish = useCallback(
    ({ message }: { message: unknown }) => {
      console.log('[AssistantRuntime] handleFinish called with message:', message)

      // Capture conversation_id and run_id from message metadata (emitted by backend)
      if (!hasMetadata(message)) {
        console.log('[AssistantRuntime] No metadata found on message')
        return
      }

      console.log('[AssistantRuntime] Message metadata:', message.metadata)

      const respConvId = message.metadata.conversationId
      const respRunId = message.metadata.runId
      const respAssistantMsgId = message.metadata.assistantMessageId

      console.log('[AssistantRuntime] Extracted - convId:', respConvId, 'runId:', respRunId, 'msgId:', respAssistantMsgId)

      // Update run ID for timeline display
      if (respRunId) {
        console.log('[AssistantRuntime] Setting activeRunId:', respRunId)
        setActiveRunId(respRunId)
      }

      // Capture the message ID mapping for feedback
      // The message object should have an 'id' property from assistant-ui
      const internalMessageId =
        typeof message === 'object' && message !== null && 'id' in message
          ? (message as { id: string }).id
          : null

      if (internalMessageId && respAssistantMsgId && respConvId) {
        messageIdMapRef.current.set(internalMessageId, {
          conversationId: respConvId,
          messageId: respAssistantMsgId,
        })
      }

      if (respConvId && respConvId !== conversationIdRef.current) {
        conversationIdRef.current = respConvId
        setActiveConversationId(respConvId)
        onConversationCreated?.(respConvId)

        // Optimistic update: immediately show the conversation in the sidebar
        // Use 'pointer' scope type if we have a pointerId, otherwise 'user' scope
        const hasPointer = !!pointerIdRef.current
        addConversation({
          id: respConvId,
          tenant_id: '',
          user_id: '',
          scope_type: hasPointer ? 'pointer' : 'user',
          scope_id: hasPointer ? pointerIdRef.current! : null,
          module: moduleRef.current,
          title: 'New conversation',
          status: 'active',
          message_count: 1,
          total_input_tokens: 0,
          total_output_tokens: 0,
          total_cost_micros: 0,
          session_id: sessionIdRef.current,
          run_id: respRunId ?? null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_message_at: new Date().toISOString(),
        })

        // Refresh conversations list so sidebar updates with real data
        queryClient.invalidateQueries({ queryKey: ['conversations'] })
      }
    },
    [setActiveConversationId, setActiveRunId, addConversation, onConversationCreated, queryClient]
  )

  // Feedback adapter for thumbs up/down on assistant messages
  // Maps assistant-ui internal message IDs to backend UUIDs and calls our API
  const feedbackAdapter: FeedbackAdapter = useMemo(
    () => ({
      submit: async (feedback) => {
        // feedback.message is the ThreadMessage object with an id property
        const internalId = feedback.message.id
        const mapping = messageIdMapRef.current.get(internalId)
        if (!mapping) {
          // If we don't have a mapping, the message may be from a previous session
          // or the metadata wasn't captured. Log and return silently.
          console.warn(
            `[FeedbackAdapter] No backend mapping for message ${internalId}`
          )
          return
        }

        const { conversationId, messageId } = mapping
        const rating = feedback.type === 'positive' ? 'positive' : 'negative'

        try {
          await conversationsApi.addFeedback(conversationId, messageId, { rating })
        } catch (error) {
          // 409 Conflict means feedback already exists, which is fine
          if (error instanceof Error && error.message.includes('409')) {
            return
          }
          console.error('[FeedbackAdapter] Failed to submit feedback:', error)
        }
      },
    }),
    []
  )

  const runtime = useChatRuntime({
    transport,
    onFinish: handleFinish,
    adapters: {
      feedback: feedbackAdapter,
    },
  })

  return <AssistantRuntimeProvider runtime={runtime}>{children}</AssistantRuntimeProvider>
}
