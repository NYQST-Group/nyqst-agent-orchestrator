import { describe, it, expect, vi, beforeEach, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { conversationsApi } from '@/api/conversations'

// Mock the auth store
vi.mock('@/stores/auth-store', () => ({
  getAuthHeaders: vi.fn(() => ({ Authorization: 'Bearer test-token' })),
}))

const server = setupServer()

beforeEach(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

afterEach(() => {
  server.resetHandlers()
})

afterAll(() => {
  server.close()
})

// Helper to capture request details - avoids TypeScript 'never' narrowing issue
interface RequestCapture {
  url?: URL
  path?: string
  headers?: Headers
  body?: unknown
}

describe('conversationsApi', () => {
  describe('list', () => {
    it('test_list_conversations_sends_query_params', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/conversations', ({ request }) => {
          capture.url = new URL(request.url)
          capture.headers = request.headers
          return HttpResponse.json({ items: [], total: 0 })
        })
      )

      await conversationsApi.list({
        scope_type: 'tenant',
        module: 'chat',
        status: 'active',
        session_id: 'sess-123',
        limit: 20,
        offset: 10,
      })

      expect(capture.url?.searchParams.get('scope_type')).toBe('tenant')
      expect(capture.url?.searchParams.get('module')).toBe('chat')
      expect(capture.url?.searchParams.get('status')).toBe('active')
      expect(capture.url?.searchParams.get('session_id')).toBe('sess-123')
      expect(capture.url?.searchParams.get('limit')).toBe('20')
      expect(capture.url?.searchParams.get('offset')).toBe('10')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })

    it('test_list_conversations_without_params', async () => {
      server.use(
        http.get('/api/v1/conversations', () => {
          return HttpResponse.json({
            items: [
              {
                id: 'conv-1',
                title: 'Test Conversation',
                status: 'active',
              },
            ],
            total: 1,
          })
        })
      )

      const result = await conversationsApi.list()

      expect(result.items).toHaveLength(1)
      expect(result.total).toBe(1)
    })
  })

  describe('get', () => {
    it('test_get_conversation_by_id', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/conversations/:id', ({ request, params }) => {
          capture.path = `/api/v1/conversations/${params.id}`
          capture.headers = request.headers
          return HttpResponse.json({
            id: params.id,
            title: 'Test Conversation',
            status: 'active',
            message_count: 5,
          })
        })
      )

      const result = await conversationsApi.get('conv-123')

      expect(capture.path).toBe('/api/v1/conversations/conv-123')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(result.id).toBe('conv-123')
      expect(result.title).toBe('Test Conversation')
    })
  })

  describe('create', () => {
    it('test_create_conversation_sends_body', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/conversations', async ({ request }) => {
          capture.body = await request.json()
          capture.headers = request.headers
          return HttpResponse.json(
            {
              id: 'conv-new',
              title: 'New Conversation',
              status: 'active',
              ...(capture.body as object),
            },
            { status: 201 }
          )
        })
      )

      const conversationData = {
        scope_type: 'tenant',
        scope_id: 'tenant-1',
        module: 'chat',
        title: 'New Conversation',
        session_id: 'sess-123',
      }

      const result = await conversationsApi.create(conversationData)

      expect(capture.body).toEqual(conversationData)
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(result.id).toBe('conv-new')
    })
  })

  describe('update', () => {
    it('test_update_conversation_sends_patch', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.patch('/api/v1/conversations/:id', async ({ request, params }) => {
          capture.body = await request.json()
          capture.path = `/api/v1/conversations/${params.id}`
          capture.headers = request.headers
          const body = capture.body as { title?: string; status?: string }
          return HttpResponse.json({
            id: params.id,
            title: body.title,
            status: body.status || 'active',
          })
        })
      )

      const updateData = {
        title: 'Updated Title',
        status: 'archived',
      }

      const result = await conversationsApi.update('conv-123', updateData)

      expect(capture.path).toBe('/api/v1/conversations/conv-123')
      expect(capture.body).toEqual(updateData)
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(result.title).toBe('Updated Title')
    })
  })

  describe('delete', () => {
    it('test_delete_conversation_sends_delete', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.delete('/api/v1/conversations/:id', ({ request, params }) => {
          capture.path = `/api/v1/conversations/${params.id}`
          capture.headers = request.headers
          return new HttpResponse(null, { status: 204 })
        })
      )

      await conversationsApi.delete('conv-123')

      expect(capture.path).toBe('/api/v1/conversations/conv-123')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })
  })

  describe('getMessages', () => {
    it('test_get_messages_with_pagination', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/conversations/:id/messages', ({ request, params }) => {
          capture.url = new URL(request.url)
          capture.path = `/api/v1/conversations/${params.id}/messages`
          capture.headers = request.headers
          return HttpResponse.json({
            items: [
              {
                id: 'msg-1',
                role: 'user',
                content: 'Hello',
                sequence_number: 1,
              },
            ],
            total: 1,
          })
        })
      )

      const result = await conversationsApi.getMessages('conv-123', {
        limit: 50,
        before_seq: 100,
      })

      expect(capture.path).toBe('/api/v1/conversations/conv-123/messages')
      expect(capture.url?.searchParams.get('limit')).toBe('50')
      expect(capture.url?.searchParams.get('before_seq')).toBe('100')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(result.items).toHaveLength(1)
    })

    it('test_get_messages_without_params', async () => {
      server.use(
        http.get('/api/v1/conversations/:id/messages', () => {
          return HttpResponse.json({ items: [], total: 0 })
        })
      )

      const result = await conversationsApi.getMessages('conv-123')
      expect(result.items).toHaveLength(0)
    })
  })

  describe('addFeedback', () => {
    it('test_add_feedback_sends_post', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post(
          '/api/v1/conversations/:convId/messages/:msgId/feedback',
          async ({ request, params }) => {
            capture.body = await request.json()
            capture.path = `/api/v1/conversations/${params.convId}/messages/${params.msgId}/feedback`
            capture.headers = request.headers
            const body = capture.body as { rating: string; content?: string }
            return HttpResponse.json(
              {
                id: 'fb-1',
                rating: body.rating,
                content: body.content,
                created_at: '2024-01-01T00:00:00Z',
              },
              { status: 201 }
            )
          }
        )
      )

      const feedbackData = {
        rating: 'positive',
        content: 'Great response!',
      }

      const result = await conversationsApi.addFeedback('conv-123', 'msg-456', feedbackData)

      expect(capture.path).toBe('/api/v1/conversations/conv-123/messages/msg-456/feedback')
      expect(capture.body).toEqual(feedbackData)
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(result.rating).toBe('positive')
    })
  })

  describe('branch', () => {
    it('test_branch_sends_message_id', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/conversations/:convId/branch', async ({ request, params }) => {
          capture.body = await request.json()
          capture.path = `/api/v1/conversations/${params.convId}/branch`
          capture.headers = request.headers
          const body = capture.body as { message_id: string }
          return HttpResponse.json({
            conversation_id: 'conv-new',
            branch_point_message_id: body.message_id,
            new_sequence_number: 1,
          })
        })
      )

      const result = await conversationsApi.branch('conv-123', 'msg-456')

      expect(capture.path).toBe('/api/v1/conversations/conv-123/branch')
      expect(capture.body).toEqual({ message_id: 'msg-456' })
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(result.branch_point_message_id).toBe('msg-456')
    })
  })

  describe('getSiblings', () => {
    it('test_get_siblings', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get(
          '/api/v1/conversations/:convId/messages/:msgId/siblings',
          ({ request, params }) => {
            capture.path = `/api/v1/conversations/${params.convId}/messages/${params.msgId}/siblings`
            capture.headers = request.headers
            return HttpResponse.json({
              items: [
                {
                  id: 'msg-456',
                  sequence_number: 5,
                  role: 'assistant',
                  created_at: '2024-01-01T00:00:00Z',
                },
                {
                  id: 'msg-789',
                  sequence_number: 5,
                  role: 'assistant',
                  created_at: '2024-01-01T00:01:00Z',
                },
              ],
              total: 2,
              current_index: 0,
            })
          }
        )
      )

      const result = await conversationsApi.getSiblings('conv-123', 'msg-456')

      expect(capture.path).toBe('/api/v1/conversations/conv-123/messages/msg-456/siblings')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(result.current_index).toBe(0)
      expect(result.items).toHaveLength(2)
    })
  })
})
