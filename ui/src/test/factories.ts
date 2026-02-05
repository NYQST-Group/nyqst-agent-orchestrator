/**
 * Test data factories for frontend tests.
 *
 * Provides builders for UIMessage, AgentSource, Pointer, and other
 * domain objects used across hook and component tests.
 */

import type { UIMessage } from '@ai-sdk/react'
import type { AgentSource } from '@/components/chat/SourcesSidebar'

let idCounter = 0
function nextId(): string {
  return `test-id-${++idCounter}`
}

export function makeUIMessage(
  overrides: Partial<UIMessage> & { text?: string } = {}
): UIMessage {
  const { text = 'Hello', ...rest } = overrides
  return {
    id: nextId(),
    role: 'user' as const,
    parts: [{ type: 'text' as const, text }],
    ...rest,
  } as UIMessage
}

export function makeAssistantMessage(
  text: string,
  sources: Array<{
    sourceId: string
    title: string
    content?: string
    score?: number
    artifact_sha256?: string
    chunk_index?: number
  }> = []
): UIMessage {
  const parts: UIMessage['parts'] = []

  // Source-document parts come before text in AI SDK v3
  for (const src of sources) {
    parts.push({
      type: 'source-document' as const,
      sourceId: src.sourceId,
      mediaType: 'text/plain',
      title: src.title,
      providerMetadata: {
        custom: {
          content: src.content ?? '',
          score: src.score ?? 0.9,
          artifact_sha256: src.artifact_sha256 ?? 'abc123',
          chunk_index: src.chunk_index ?? 0,
        },
      },
    } as any)
  }

  parts.push({ type: 'text' as const, text })

  return {
    id: nextId(),
    role: 'assistant' as const,
    parts,
  } as UIMessage
}

export function makeAgentSource(overrides: Partial<AgentSource> = {}): AgentSource {
  return {
    chunk_id: nextId(),
    artifact_sha256: 'abc123def456',
    chunk_index: 0,
    content: 'Test source content',
    score: 0.92,
    path_hint: 'docs/test.pdf',
    ...overrides,
  }
}

export function makePointer(
  overrides: Partial<import('@/types/api').Pointer> = {}
): import('@/types/api').Pointer {
  return {
    id: nextId(),
    namespace: 'test',
    name: 'Test Notebook',
    pointer_type: 'bundle',
    manifest_sha256: 'a'.repeat(64),
    metadata: {},
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  }
}

export function makeConversation(
  overrides: Partial<import('@/types/conversations').ConversationResponse> = {}
): import('@/types/conversations').ConversationResponse {
  return {
    id: nextId(),
    tenant_id: 'tenant-1',
    user_id: 'user-1',
    scope_type: 'tenant',
    scope_id: null,
    module: 'research',
    title: 'Test Conversation',
    status: 'active',
    message_count: 0,
    total_input_tokens: 0,
    total_output_tokens: 0,
    total_cost_micros: 0,
    session_id: null,
    run_id: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_message_at: null,
    ...overrides,
  }
}

export function makeMessage(
  overrides: Partial<import('@/types/conversations').MessageResponse> = {}
): import('@/types/conversations').MessageResponse {
  return {
    id: nextId(),
    conversation_id: 'conv-1',
    role: 'user',
    content: 'Test message',
    parts: null,
    input_tokens: null,
    output_tokens: null,
    cost_micros: null,
    latency_ms: null,
    model_id: null,
    status: 'complete',
    parent_message_id: null,
    sequence_number: 1,
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

export function makeSession(
  overrides: Partial<import('@/types/sessions').SessionResponse> = {}
): import('@/types/sessions').SessionResponse {
  return {
    id: nextId(),
    tenant_id: 'tenant-1',
    user_id: 'user-1',
    scope_type: 'tenant',
    scope_id: null,
    module: null,
    objective: null,
    status: 'active',
    total_cost_micros: 0,
    idle_timeout_minutes: 30,
    started_at: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_active_at: new Date().toISOString(),
    closed_at: null,
    close_reason: null,
    ...overrides,
  }
}

/** Reset the ID counter between test suites if needed */
export function resetIdCounter() {
  idCounter = 0
}
