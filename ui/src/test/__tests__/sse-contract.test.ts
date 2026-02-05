/**
 * Contract tests: Adapter SSE → DefaultChatTransport → UIMessage
 *
 * These tests verify that our Python adapter's SSE output format is correctly
 * parsed by AI SDK's DefaultChatTransport into UIMessage objects with the
 * expected parts structure. If either side changes the wire format, these
 * tests catch the mismatch.
 *
 * @vitest-environment node
 */

import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { DefaultChatTransport } from 'ai'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build an SSE response from an array of event JSON objects. */
function sseResponse(events: Record<string, unknown>[]) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    start(controller) {
      for (const evt of events) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(evt)}\n\n`))
      }
      controller.close()
    },
  })
  return new HttpResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'X-Vercel-AI-UI-Message-Stream': 'v1',
      'X-Run-Id': 'contract-test',
    },
  })
}

/** Minimal event lifecycle wrapping inner events. */
function wrapLifecycle(inner: Record<string, unknown>[]) {
  return [
    { type: 'start' },
    { type: 'start-step' },
    ...inner,
    { type: 'finish-step' },
    { type: 'finish' },
  ]
}

/** Consume a DefaultChatTransport stream and collect all UIMessageChunk parts. */
async function consumeStream(transport: DefaultChatTransport<any>) {
  const stream = await transport.sendMessages({
    trigger: 'submit-message' as const,
    chatId: 'test-chat',
    messageId: undefined,
    messages: [{ id: 'u1', role: 'user', parts: [{ type: 'text', text: 'hello' }], createdAt: new Date() }],
    body: {},
    headers: {},
    abortSignal: new AbortController().signal,
  })

  const parts: any[] = []
  const reader = stream.getReader()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    parts.push(value)
  }
  return parts
}

// ---------------------------------------------------------------------------
// MSW server
// ---------------------------------------------------------------------------

const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// ---------------------------------------------------------------------------
// Contract tests
// ---------------------------------------------------------------------------

describe('SSE Contract: Adapter → DefaultChatTransport', () => {
  const transport = new DefaultChatTransport<any>({ api: 'http://localhost/api/v1/agent/chat' })

  it('text-only stream produces text parts', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'Hello world' },
            { type: 'text-end', id: 'text-1' },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    const textParts = parts.filter((p: any) => p.type === 'text-delta')
    expect(textParts.length).toBeGreaterThan(0)
    expect(textParts.map((p: any) => p.delta).join('')).toBe('Hello world')
  })

  it('source-document event produces source part with providerMetadata', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            {
              type: 'source-document',
              sourceId: 'chunk-42',
              title: 'report.pdf',
              mediaType: 'text/plain',
              providerMetadata: {
                custom: {
                  artifact_sha256: 'deadbeef',
                  chunk_index: 3,
                  content: 'Excerpt text',
                  score: 0.88,
                },
              },
            },
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'Answer' },
            { type: 'text-end', id: 'text-1' },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    const sourceParts = parts.filter((p: any) => p.type === 'source-document')
    expect(sourceParts).toHaveLength(1)
    expect(sourceParts[0]).toMatchObject({
      type: 'source-document',
      sourceId: 'chunk-42',
      title: 'report.pdf',
    })
    expect(sourceParts[0].providerMetadata?.custom).toMatchObject({
      artifact_sha256: 'deadbeef',
      chunk_index: 3,
      content: 'Excerpt text',
      score: 0.88,
    })
  })

  it('sources arrive before text in part order', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            {
              type: 'source-document',
              sourceId: 'c1',
              title: 'doc.pdf',
              mediaType: 'text/plain',
              providerMetadata: { custom: { content: 'x', score: 0.9, artifact_sha256: 'a', chunk_index: 0 } },
            },
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'Response' },
            { type: 'text-end', id: 'text-1' },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    const sourceIdx = parts.findIndex((p: any) => p.type === 'source-document')
    const textIdx = parts.findIndex((p: any) => p.type === 'text-delta')
    expect(sourceIdx).toBeGreaterThanOrEqual(0)
    expect(textIdx).toBeGreaterThan(sourceIdx)
  })

  it('missing providerMetadata fields default gracefully', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            {
              type: 'source-document',
              sourceId: 'c1',
              title: 'minimal.pdf',
              mediaType: 'text/plain',
              providerMetadata: { custom: {} },
            },
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'OK' },
            { type: 'text-end', id: 'text-1' },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    const sourceParts = parts.filter((p: any) => p.type === 'source-document')
    expect(sourceParts).toHaveLength(1)
    // The SDK passes through whatever providerMetadata.custom contains —
    // our app's extractSources() handles defaults. Here we verify the SDK
    // doesn't reject an empty custom object.
    expect(sourceParts[0].providerMetadata?.custom).toEqual({})
  })

  it('complete event lifecycle parses without errors', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'A' },
            { type: 'text-delta', id: 'text-1', delta: 'B' },
            { type: 'text-delta', id: 'text-1', delta: 'C' },
            { type: 'text-end', id: 'text-1' },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    // Should contain start, text deltas, and finish without throwing
    const textContent = parts
      .filter((p: any) => p.type === 'text-delta')
      .map((p: any) => p.delta)
      .join('')
    expect(textContent).toBe('ABC')
  })

  it('tool-input-start event is parseable', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            { type: 'tool-input-start', toolCallId: 'tc-1', toolName: 'search_documents' },
            { type: 'tool-input-delta', toolCallId: 'tc-1', inputTextDelta: '{"query":"test"}' },
            { type: 'tool-input-available', toolCallId: 'tc-1', toolName: 'search_documents', input: { query: 'test' } },
            { type: 'tool-output-available', toolCallId: 'tc-1', output: 'Found 3 results' },
          ])
        )
      )
    )

    // Should parse without errors
    const parts = await consumeStream(transport)
    expect(parts.length).toBeGreaterThan(0)
  })

  it('tool events coexist with text events', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            { type: 'tool-input-start', toolCallId: 'tc-1', toolName: 'search_documents' },
            { type: 'tool-input-available', toolCallId: 'tc-1', toolName: 'search_documents', input: { query: 'risks' } },
            { type: 'tool-output-available', toolCallId: 'tc-1', output: 'Found docs' },
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'Based on the results...' },
            { type: 'text-end', id: 'text-1' },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    const textParts = parts.filter((p: any) => p.type === 'text-delta')
    expect(textParts.length).toBeGreaterThan(0)
    expect(textParts.map((p: any) => p.delta).join('')).toBe('Based on the results...')
  })

  it('multi-step events with text in both steps', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse([
          { type: 'start' },
          { type: 'start-step' },
          { type: 'text-start', id: 'text-1' },
          { type: 'text-delta', id: 'text-1', delta: 'Step 1' },
          { type: 'text-end', id: 'text-1' },
          { type: 'finish-step' },
          { type: 'start-step' },
          { type: 'text-start', id: 'text-2' },
          { type: 'text-delta', id: 'text-2', delta: 'Step 2' },
          { type: 'text-end', id: 'text-2' },
          { type: 'finish-step' },
          { type: 'finish' },
        ])
      )
    )

    const parts = await consumeStream(transport)
    // Both steps' text should be present
    const textContent = parts
      .filter((p: any) => p.type === 'text-delta')
      .map((p: any) => p.delta)
      .join('')
    expect(textContent).toContain('Step 1')
    expect(textContent).toContain('Step 2')
  })

  it('finish event with messageMetadata is parsed correctly', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse(
          wrapLifecycle([
            { type: 'text-start', id: 'text-1' },
            { type: 'text-delta', id: 'text-1', delta: 'Response text' },
            { type: 'text-end', id: 'text-1' },
            {
              type: 'finish',
              messageMetadata: {
                conversationId: 'conv-123',
                runId: 'run-456',
                outputTokens: 42,
                inputTokens: 10,
                latencyMs: 1500,
              },
            },
          ])
        )
      )
    )

    const parts = await consumeStream(transport)
    // Check if finish event has messageMetadata
    const finishPart = parts.find((p: any) => p.type === 'finish')
    expect(finishPart).toBeDefined()
    expect(finishPart?.messageMetadata).toBeDefined()
    expect(finishPart?.messageMetadata).toMatchObject({
      conversationId: 'conv-123',
      runId: 'run-456',
      outputTokens: 42,
      inputTokens: 10,
      latencyMs: 1500,
    })
  })

  it('message metadata from finish event is included in message parts stream', async () => {
    server.use(
      http.post('http://localhost/api/v1/agent/chat', () =>
        sseResponse([
          { type: 'start' },
          { type: 'start-step' },
          { type: 'text-start', id: 'text-1' },
          { type: 'text-delta', id: 'text-1', delta: 'Test response' },
          { type: 'text-end', id: 'text-1' },
          { type: 'finish-step' },
          {
            type: 'finish',
            messageMetadata: {
              conversationId: 'conv-abc',
              runId: 'run-xyz',
              outputTokens: 100,
              inputTokens: 50,
              latencyMs: 2000,
            },
          },
        ])
      )
    )

    const parts = await consumeStream(transport)

    // Look for the finish part (it should be the last part)
    const finishPart = parts[parts.length - 1]
    expect(finishPart?.type).toBe('finish')

    // The finish part should have messageMetadata
    expect(finishPart?.messageMetadata).toBeDefined()
    expect(finishPart?.messageMetadata).toMatchObject({
      conversationId: 'conv-abc',
      runId: 'run-xyz',
      outputTokens: 100,
      inputTokens: 50,
      latencyMs: 2000,
    })
  })
})
