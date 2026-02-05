import { describe, it, expect, vi, beforeEach, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { sessionsApi } from '@/api/sessions'

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

describe('sessionsApi', () => {
  describe('create', () => {
    it('test_create_session_sends_post', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/sessions', async ({ request }) => {
          capture.body = await request.json()
          capture.headers = request.headers
          return HttpResponse.json(
            {
              id: 'sess-new',
              tenant_id: 'tenant-1',
              user_id: 'user-1',
              status: 'active',
              ...(capture.body as object),
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
            },
            { status: 201 }
          )
        })
      )

      const sessionData = {
        scope_type: 'tenant',
        scope_id: 'tenant-1',
        module: 'chat',
        objective: 'Complete project setup',
        idle_timeout_minutes: 30,
      }

      const result = await sessionsApi.create(sessionData)

      expect(capture.body).toEqual(sessionData)
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(result.id).toBe('sess-new')
      expect(result.status).toBe('active')
    })

    it('test_create_session_with_minimal_data', async () => {
      server.use(
        http.post('/api/v1/sessions', () => {
          return HttpResponse.json(
            {
              id: 'sess-minimal',
              status: 'active',
              created_at: '2024-01-01T00:00:00Z',
            },
            { status: 201 }
          )
        })
      )

      const result = await sessionsApi.create({})

      expect(result.id).toBe('sess-minimal')
    })
  })

  describe('list', () => {
    it('test_list_sessions_with_params', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/sessions', ({ request }) => {
          capture.url = new URL(request.url)
          capture.headers = request.headers
          return HttpResponse.json({
            items: [
              {
                id: 'sess-1',
                status: 'active',
                created_at: '2024-01-01T00:00:00Z',
              },
            ],
            total: 1,
          })
        })
      )

      const result = await sessionsApi.list({
        status: 'active',
        limit: 25,
        offset: 5,
      })

      expect(capture.url?.searchParams.get('status')).toBe('active')
      expect(capture.url?.searchParams.get('limit')).toBe('25')
      expect(capture.url?.searchParams.get('offset')).toBe('5')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(result.items).toHaveLength(1)
      expect(result.total).toBe(1)
    })

    it('test_list_sessions_without_params', async () => {
      server.use(
        http.get('/api/v1/sessions', () => {
          return HttpResponse.json({
            items: [],
            total: 0,
          })
        })
      )

      const result = await sessionsApi.list()

      expect(result.items).toHaveLength(0)
    })
  })

  describe('get', () => {
    it('test_get_session_by_id', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/sessions/:id', ({ request, params }) => {
          capture.path = `/api/v1/sessions/${params.id}`
          capture.headers = request.headers
          return HttpResponse.json({
            id: params.id,
            tenant_id: 'tenant-1',
            user_id: 'user-1',
            scope_type: 'tenant',
            scope_id: 'tenant-1',
            module: 'chat',
            objective: 'Complete project',
            status: 'active',
            started_at: '2024-01-01T00:00:00Z',
            last_active_at: '2024-01-01T00:00:00Z',
            idle_timeout_minutes: 30,
            closed_at: null,
            close_reason: null,
            total_cost_micros: 50000,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          })
        })
      )

      const result = await sessionsApi.get('sess-123')

      expect(capture.path).toBe('/api/v1/sessions/sess-123')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(result.id).toBe('sess-123')
      expect(result.status).toBe('active')
      expect(result.total_cost_micros).toBe(50000)
    })
  })

  describe('updateStatus', () => {
    it('test_update_status_sends_patch', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.patch('/api/v1/sessions/:id', async ({ request, params }) => {
          capture.body = await request.json()
          capture.path = `/api/v1/sessions/${params.id}`
          capture.headers = request.headers
          const body = capture.body as { status?: string; close_reason?: string }
          return HttpResponse.json({
            id: params.id,
            status: body.status,
            close_reason: body.close_reason,
            updated_at: '2024-01-01T00:00:00Z',
          })
        })
      )

      const statusData = {
        status: 'closed',
        close_reason: 'completed',
      }

      const result = await sessionsApi.updateStatus('sess-123', statusData)

      expect(capture.path).toBe('/api/v1/sessions/sess-123')
      expect(capture.body).toEqual(statusData)
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(result.status).toBe('closed')
      expect(result.close_reason).toBe('completed')
    })

    it('test_update_status_without_close_reason', async () => {
      server.use(
        http.patch('/api/v1/sessions/:id', async ({ request }) => {
          const body = (await request.json()) as { status?: string }
          return HttpResponse.json({
            id: 'sess-123',
            status: body.status,
          })
        })
      )

      const result = await sessionsApi.updateStatus('sess-123', { status: 'paused' })

      expect(result.status).toBe('paused')
    })
  })

  describe('getCost', () => {
    it('test_get_cost_by_id', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/sessions/:id/cost', ({ request, params }) => {
          capture.path = `/api/v1/sessions/${params.id}/cost`
          capture.headers = request.headers
          return HttpResponse.json({
            session_id: params.id,
            total_cost_micros: 150000,
            conversation_count: 2,
            total_input_tokens: 5000,
            total_output_tokens: 10000,
            conversations: [
              {
                id: 'conv-1',
                title: 'Test Conversation',
                cost_micros: 100000,
                input_tokens: 3000,
                output_tokens: 6000,
              },
              {
                id: 'conv-2',
                title: 'Another Conversation',
                cost_micros: 50000,
                input_tokens: 2000,
                output_tokens: 4000,
              },
            ],
          })
        })
      )

      const result = await sessionsApi.getCost('sess-123')

      expect(capture.path).toBe('/api/v1/sessions/sess-123/cost')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(result.session_id).toBe('sess-123')
      expect(result.total_cost_micros).toBe(150000)
      expect(result.conversations).toHaveLength(2)
      expect(result.conversations[0].id).toBe('conv-1')
      expect(result.conversations[0].cost_micros).toBe(100000)
    })
  })
})
