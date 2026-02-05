/**
 * Unit tests for NyqstAssistantProvider.
 *
 * Tests the handleFinish callback logic that captures conversation IDs
 * from message metadata and updates the conversation store.
 * Also tests the DefaultChatTransport configuration.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { NyqstAssistantProvider } from '@/providers/assistant-runtime'
import { useConversationStore } from '@/stores/conversation-store'

// Capture the transport options for testing
let capturedTransportOptions: {
  api?: string
  headers?: () => Record<string, string>
  prepareSendMessagesRequest?: (args: {
    messages: Array<{ role: string; parts: Array<{ type: string; text: string }> }>
    body: Record<string, unknown>
  }) => { body: Record<string, unknown> }
} | null = null

// Mock DefaultChatTransport to capture constructor options
vi.mock('ai', () => ({
  DefaultChatTransport: class MockDefaultChatTransport {
    constructor(options: typeof capturedTransportOptions) {
      capturedTransportOptions = options
    }
  },
}))

// Mock the useChatRuntime hook
const mockOnFinish = vi.fn()
vi.mock('@assistant-ui/react-ai-sdk', () => ({
  useChatRuntime: vi.fn(({ onFinish }) => {
    // Store the onFinish callback for testing
    mockOnFinish.mockImplementation(onFinish)
    return { subscribe: vi.fn() }
  }),
}))

// Mock AssistantRuntimeProvider to just render children
vi.mock('@assistant-ui/react', () => ({
  AssistantRuntimeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

// Mock the auth store
vi.mock('@/stores/auth-store', () => ({
  getAuthHeaders: () => ({ Authorization: 'Bearer test-token', 'X-Tenant-ID': 'tenant-123' }),
}))

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
}

function renderProvider(props: Partial<React.ComponentProps<typeof NyqstAssistantProvider>> = {}) {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <NyqstAssistantProvider module="research" {...props}>
        <div data-testid="children">Test children</div>
      </NyqstAssistantProvider>
    </QueryClientProvider>
  )
}

describe('NyqstAssistantProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    capturedTransportOptions = null
    useConversationStore.getState().clear()
  })

  describe('rendering', () => {
    it('renders children', () => {
      renderProvider()
      expect(screen.getByTestId('children')).toBeInTheDocument()
    })

    it('accepts module prop', () => {
      renderProvider({ module: 'analysis' })
      expect(screen.getByTestId('children')).toBeInTheDocument()
    })

    it('accepts scopeContext prop', () => {
      renderProvider({
        scopeContext: {
          pointerId: 'ptr-123',
          manifestSha256: 'abc123',
        },
      })
      expect(screen.getByTestId('children')).toBeInTheDocument()
    })
  })

  describe('handleFinish callback', () => {
    it('captures conversation_id from message metadata and updates store', async () => {
      const onConversationCreated = vi.fn()
      renderProvider({ onConversationCreated })

      // Simulate the onFinish callback being called with a message containing conversationId
      const message = {
        id: 'msg-1',
        metadata: {
          conversationId: 'conv-new-123',
        },
      }

      // Call the captured onFinish handler
      mockOnFinish({ message })

      await waitFor(() => {
        expect(useConversationStore.getState().activeConversationId).toBe('conv-new-123')
      })
    })

    it('calls onConversationCreated callback with new conversation ID', async () => {
      const onConversationCreated = vi.fn()
      renderProvider({ onConversationCreated })

      const message = {
        metadata: { conversationId: 'conv-callback-test' },
      }

      mockOnFinish({ message })

      await waitFor(() => {
        expect(onConversationCreated).toHaveBeenCalledWith('conv-callback-test')
      })
    })

    it('does not update store when conversation_id is unchanged', async () => {
      // Set an existing conversation ID
      useConversationStore.getState().setActiveConversationId('conv-existing')

      const onConversationCreated = vi.fn()
      renderProvider({ onConversationCreated })

      // Simulate receiving the same conversation ID
      const message = {
        metadata: { conversationId: 'conv-existing' },
      }

      mockOnFinish({ message })

      // Should not trigger callback since ID is the same
      expect(onConversationCreated).not.toHaveBeenCalled()
    })

    it('adds optimistic conversation entry with correct fields', async () => {
      renderProvider({ module: 'analysis' })

      const message = {
        metadata: { conversationId: 'conv-optimistic' },
      }

      mockOnFinish({ message })

      await waitFor(() => {
        const conversations = useConversationStore.getState().conversations
        const added = conversations.find((c) => c.id === 'conv-optimistic')
        expect(added).toBeDefined()
        expect(added?.module).toBe('analysis')
        expect(added?.status).toBe('active')
        expect(added?.title).toBe('New conversation')
      })
    })

    it('handles missing metadata gracefully without throwing', () => {
      renderProvider()

      // Message with no metadata
      expect(() => mockOnFinish({ message: {} })).not.toThrow()
      expect(() => mockOnFinish({ message: null })).not.toThrow()
      expect(() => mockOnFinish({ message: { metadata: null } })).not.toThrow()
    })

    it('handles missing conversationId in metadata gracefully', () => {
      const onConversationCreated = vi.fn()
      renderProvider({ onConversationCreated })

      const message = {
        metadata: { someOtherField: 'value' },
      }

      expect(() => mockOnFinish({ message })).not.toThrow()
      expect(onConversationCreated).not.toHaveBeenCalled()
    })
  })

  describe('transport configuration', () => {
    it('configures transport with correct API endpoint', () => {
      renderProvider()

      expect(capturedTransportOptions).not.toBeNull()
      expect(capturedTransportOptions?.api).toBe('/api/v1/agent/chat')
    })

    it('includes auth headers via getAuthHeaders', () => {
      renderProvider()

      expect(capturedTransportOptions?.headers).toBeDefined()
      const headers = capturedTransportOptions?.headers?.()
      expect(headers).toEqual({
        Authorization: 'Bearer test-token',
        'X-Tenant-ID': 'tenant-123',
      })
    })

    it('prepareSendMessagesRequest formats messages correctly', () => {
      renderProvider({ module: 'research' })

      expect(capturedTransportOptions?.prepareSendMessagesRequest).toBeDefined()

      const mockMessages = [
        {
          role: 'user',
          parts: [{ type: 'text', text: 'What is the lease term?' }],
        },
      ]

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: mockMessages,
        body: {},
      })

      expect(result?.body).toBeDefined()
      expect(result?.body.messages).toEqual([
        { role: 'user', content: 'What is the lease term?' },
      ])
    })

    it('includes module in request body', () => {
      renderProvider({ module: 'analysis' })

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: [{ role: 'user', parts: [{ type: 'text', text: 'Test' }] }],
        body: {},
      })

      expect(result?.body.module).toBe('analysis')
    })

    it('includes pointer_id and manifest_sha256 from scopeContext', () => {
      renderProvider({
        module: 'research',
        scopeContext: {
          pointerId: 'ptr-456',
          manifestSha256: 'sha256-abc',
        },
      })

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: [{ role: 'user', parts: [{ type: 'text', text: 'Test' }] }],
        body: {},
      })

      expect(result?.body.pointer_id).toBe('ptr-456')
      expect(result?.body.manifest_sha256).toBe('sha256-abc')
    })

    it('includes conversation_id from store when available', () => {
      useConversationStore.getState().setActiveConversationId('conv-from-store')

      renderProvider({ module: 'research' })

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: [{ role: 'user', parts: [{ type: 'text', text: 'Test' }] }],
        body: {},
      })

      expect(result?.body.conversation_id).toBe('conv-from-store')
    })

    it('includes session_id from store when available', () => {
      useConversationStore.getState().setActiveSessionId('session-from-store')

      renderProvider({ module: 'research' })

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: [{ role: 'user', parts: [{ type: 'text', text: 'Test' }] }],
        body: {},
      })

      expect(result?.body.session_id).toBe('session-from-store')
    })

    it('merges additional body params from caller', () => {
      renderProvider({ module: 'research' })

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: [{ role: 'user', parts: [{ type: 'text', text: 'Test' }] }],
        body: { customParam: 'custom-value' },
      })

      expect(result?.body.customParam).toBe('custom-value')
    })

    it('filters non-text parts from messages', () => {
      renderProvider({ module: 'research' })

      // Use type assertion to simulate the actual runtime message structure
      // which can have parts with different shapes
      const mockMessages = [
        {
          role: 'user',
          parts: [
            { type: 'text', text: 'Hello ' },
            { type: 'image', text: '' }, // Non-text parts filtered by type check
            { type: 'text', text: 'world' },
          ],
        },
      ]

      const result = capturedTransportOptions?.prepareSendMessagesRequest?.({
        messages: mockMessages,
        body: {},
      })

      // Should join only text parts (empty string from 'image' part gets filtered by .filter(p => p.type === 'text'))
      expect(result?.body.messages).toEqual([{ role: 'user', content: 'Hello world' }])
    })
  })
})
