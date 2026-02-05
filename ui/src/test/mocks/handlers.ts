/**
 * MSW request handlers for test mocking.
 *
 * Uses MSW v2+ http namespace. SSE mocking is done inline in tests
 * since MSW's sse namespace requires per-test stream control.
 */

import { http, HttpResponse } from 'msw'

/** Default handlers that return empty/success responses. */
export const handlers = [
  // Pointers list — returns empty array by default
  http.get('/api/v1/pointers', () => {
    return HttpResponse.json([])
  }),

  // Agent chat — returns a simple SSE stream by default
  http.post('/api/v1/agent/chat', () => {
    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(encoder.encode('data: {"type":"start"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"start-step"}\n\n'))
        controller.enqueue(
          encoder.encode(
            'data: {"type":"source-document","sourceId":"chunk-1","title":"report.pdf","mediaType":"text/plain","providerMetadata":{"custom":{"artifact_sha256":"abc123","chunk_index":0,"content":"Relevant excerpt from document","score":0.95}}}\n\n'
          )
        )
        controller.enqueue(encoder.encode('data: {"type":"text-start","id":"text-1"}\n\n'))
        controller.enqueue(
          encoder.encode(
            'data: {"type":"text-delta","id":"text-1","delta":"Test response"}\n\n'
          )
        )
        controller.enqueue(encoder.encode('data: {"type":"text-end","id":"text-1"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"finish-step"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"finish"}\n\n'))
        controller.close()
      },
    })

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'X-Run-Id': 'test-run-id',
        'X-Conversation-Id': 'conv-test-123',
        'X-Vercel-AI-UI-Message-Stream': 'v1',
      },
    })
  }),

  // Conversations
  http.get('/api/v1/conversations', () => {
    return HttpResponse.json({ items: [], total: 0 })
  }),

  http.post('/api/v1/conversations', () => {
    return HttpResponse.json(
      {
        id: 'conv-new',
        tenant_id: 'tenant-1',
        user_id: 'user-1',
        scope_type: 'tenant',
        title: 'New Conversation',
        status: 'active',
        message_count: 0,
        total_input_tokens: 0,
        total_output_tokens: 0,
        total_cost_micros: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { status: 201 }
    )
  }),

  http.get('/api/v1/conversations/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      title: 'Test Conversation',
      status: 'active',
      message_count: 0,
    })
  }),

  http.get('/api/v1/conversations/:id/messages', () => {
    return HttpResponse.json({ items: [], total: 0 })
  }),

  http.post('/api/v1/conversations/:convId/messages/:msgId/feedback', () => {
    return HttpResponse.json(
      { id: 'fb-1', rating: 'positive', created_at: new Date().toISOString() },
      { status: 201 }
    )
  }),

  // Sessions
  http.get('/api/v1/sessions', () => {
    return HttpResponse.json({ items: [], total: 0 })
  }),

  http.post('/api/v1/sessions', () => {
    return HttpResponse.json(
      { id: 'sess-new', status: 'active', created_at: new Date().toISOString() },
      { status: 201 }
    )
  }),

  // Tags
  http.get('/api/v1/tags', () => {
    return HttpResponse.json({ items: [], total: 0 })
  }),

  http.post('/api/v1/tags', () => {
    return HttpResponse.json(
      { id: 'tag-1', namespace: 'domain', key: 'type', value: 'test' },
      { status: 201 }
    )
  }),
]
