/**
 * Tests for tags API client.
 */

import { describe, it, expect, vi, beforeEach, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { tagsApi } from '@/api/tags'

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

// Helper to capture request details
interface RequestCapture {
  url?: URL
  headers?: Headers
  body?: unknown
  method?: string
}

describe('tagsApi', () => {
  describe('add', () => {
    it('sends POST with correct body and headers', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/tags', async ({ request }) => {
          capture.headers = request.headers
          capture.body = await request.json()
          return HttpResponse.json({
            id: 'tag-123',
            entity_type: 'conversation',
            entity_id: 'conv-456',
            namespace: 'domain',
            key: 'asset_class',
            value: 'logistics',
            source: 'manual',
            confidence: null,
            verified_by: null,
            verified_at: null,
            created_at: '2026-02-04T00:00:00Z',
          })
        })
      )

      const result = await tagsApi.add({
        entity_type: 'conversation',
        entity_id: 'conv-456',
        namespace: 'domain',
        key: 'asset_class',
        value: 'logistics',
      })

      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.headers?.get('Content-Type')).toBe('application/json')
      expect(capture.body).toEqual({
        entity_type: 'conversation',
        entity_id: 'conv-456',
        namespace: 'domain',
        key: 'asset_class',
        value: 'logistics',
      })
      expect(result.id).toBe('tag-123')
    })

    it('includes optional source and confidence when provided', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.post('/api/v1/tags', async ({ request }) => {
          capture.body = await request.json()
          return HttpResponse.json({
            id: 'tag-789',
            entity_type: 'document',
            entity_id: 'doc-123',
            namespace: 'topic',
            key: 'category',
            value: 'finance',
            source: 'agent_proposed',
            confidence: 0.85,
            verified_by: null,
            verified_at: null,
            created_at: '2026-02-04T00:00:00Z',
          })
        })
      )

      await tagsApi.add({
        entity_type: 'document',
        entity_id: 'doc-123',
        namespace: 'topic',
        key: 'category',
        value: 'finance',
        source: 'agent_proposed',
        confidence: 0.85,
      })

      expect(capture.body).toEqual({
        entity_type: 'document',
        entity_id: 'doc-123',
        namespace: 'topic',
        key: 'category',
        value: 'finance',
        source: 'agent_proposed',
        confidence: 0.85,
      })
    })
  })

  describe('remove', () => {
    it('sends DELETE to correct URL with auth headers', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.delete('/api/v1/tags/:id', ({ request }) => {
          capture.url = new URL(request.url)
          capture.headers = request.headers
          capture.method = request.method
          return new HttpResponse(null, { status: 204 })
        })
      )

      await tagsApi.remove('tag-to-delete-123')

      expect(capture.url?.pathname).toContain('/api/v1/tags/tag-to-delete-123')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
      expect(capture.method).toBe('DELETE')
    })
  })

  describe('list', () => {
    it('sends GET with query params', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/tags', ({ request }) => {
          capture.url = new URL(request.url)
          capture.headers = request.headers
          return HttpResponse.json({ items: [], total: 0 })
        })
      )

      await tagsApi.list({
        entity_type: 'conversation',
        entity_id: 'conv-456',
        namespace: 'domain',
        limit: 50,
        offset: 10,
      })

      expect(capture.url?.searchParams.get('entity_type')).toBe('conversation')
      expect(capture.url?.searchParams.get('entity_id')).toBe('conv-456')
      expect(capture.url?.searchParams.get('namespace')).toBe('domain')
      expect(capture.url?.searchParams.get('limit')).toBe('50')
      expect(capture.url?.searchParams.get('offset')).toBe('10')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })

    it('works without params', async () => {
      server.use(
        http.get('/api/v1/tags', () => {
          return HttpResponse.json({
            items: [
              {
                id: 'tag-1',
                entity_type: 'conversation',
                entity_id: 'conv-1',
                namespace: 'domain',
                key: 'asset_class',
                value: 'logistics',
                source: 'manual',
                confidence: null,
                verified_by: null,
                verified_at: null,
                created_at: '2026-02-04T00:00:00Z',
              },
            ],
            total: 1,
          })
        })
      )

      const result = await tagsApi.list()

      expect(result.items).toHaveLength(1)
      expect(result.total).toBe(1)
      expect(result.items[0].namespace).toBe('domain')
    })

    it('omits undefined params from query string', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/tags', ({ request }) => {
          capture.url = new URL(request.url)
          return HttpResponse.json({ items: [], total: 0 })
        })
      )

      await tagsApi.list({
        entity_type: 'conversation',
        namespace: undefined,
        key: undefined,
      })

      expect(capture.url?.searchParams.get('entity_type')).toBe('conversation')
      expect(capture.url?.searchParams.has('namespace')).toBe(false)
      expect(capture.url?.searchParams.has('key')).toBe(false)
    })
  })

  describe('search', () => {
    it('sends GET to search endpoint with query params', async () => {
      const capture: RequestCapture = {}

      server.use(
        http.get('/api/v1/tags/search', ({ request }) => {
          capture.url = new URL(request.url)
          capture.headers = request.headers
          return HttpResponse.json([])
        })
      )

      await tagsApi.search({
        namespace: 'domain',
        value: 'logistics',
        limit: 100,
      })

      expect(capture.url?.pathname).toBe('/api/v1/tags/search')
      expect(capture.url?.searchParams.get('namespace')).toBe('domain')
      expect(capture.url?.searchParams.get('value')).toBe('logistics')
      expect(capture.url?.searchParams.get('limit')).toBe('100')
      expect(capture.headers?.get('Authorization')).toBe('Bearer test-token')
    })

    it('returns grouped results by entity', async () => {
      server.use(
        http.get('/api/v1/tags/search', () => {
          return HttpResponse.json([
            {
              entity_type: 'conversation',
              entity_id: 'conv-1',
              tags: [
                {
                  id: 'tag-1',
                  entity_type: 'conversation',
                  entity_id: 'conv-1',
                  namespace: 'domain',
                  key: 'asset_class',
                  value: 'logistics',
                  source: 'manual',
                  confidence: null,
                  verified_by: null,
                  verified_at: null,
                  created_at: '2026-02-04T00:00:00Z',
                },
              ],
            },
            {
              entity_type: 'document',
              entity_id: 'doc-1',
              tags: [
                {
                  id: 'tag-2',
                  entity_type: 'document',
                  entity_id: 'doc-1',
                  namespace: 'domain',
                  key: 'asset_class',
                  value: 'logistics',
                  source: 'agent_proposed',
                  confidence: 0.9,
                  verified_by: null,
                  verified_at: null,
                  created_at: '2026-02-04T00:00:00Z',
                },
              ],
            },
          ])
        })
      )

      const result = await tagsApi.search({ value: 'logistics' })

      expect(result).toHaveLength(2)
      expect(result[0].entity_type).toBe('conversation')
      expect(result[0].entity_id).toBe('conv-1')
      expect(result[0].tags).toHaveLength(1)
      expect(result[1].entity_type).toBe('document')
    })
  })

  describe('error handling', () => {
    it('throws on non-OK response', async () => {
      server.use(
        http.post('/api/v1/tags', () => {
          return HttpResponse.json(
            { detail: 'Invalid tag data' },
            { status: 400 }
          )
        })
      )

      await expect(
        tagsApi.add({
          entity_type: 'invalid',
          entity_id: 'id',
          namespace: 'ns',
          key: 'k',
          value: 'v',
        })
      ).rejects.toThrow('API Error: 400 Bad Request')
    })
  })
})
