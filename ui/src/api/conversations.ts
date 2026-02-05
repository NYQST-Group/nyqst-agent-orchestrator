/**
 * API client for conversations and messages.
 */

import type {
  ConversationResponse,
  ConversationListResponse,
  MessageListResponse,
  FeedbackResponse,
  BranchResponse,
  SiblingResponse,
} from '@/types/conversations'
import { getAuthHeaders } from '@/stores/auth-store'

const API_BASE = '/api/v1'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    // Consume body to free resources, but don't need the value for error message
    try {
      await response.json()
    } catch {
      await response.text()
    }
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

function withAuth(options: RequestInit = {}): RequestInit {
  return {
    ...options,
    headers: {
      ...options.headers,
      ...getAuthHeaders(),
    },
  }
}

export const conversationsApi = {
  async list(params?: {
    scope_type?: string
    scope_id?: string
    module?: string
    status?: string
    session_id?: string
    limit?: number
    offset?: number
  }): Promise<ConversationListResponse> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) searchParams.append(k, String(v))
      })
    }
    const response = await fetch(
      `${API_BASE}/conversations?${searchParams}`,
      withAuth()
    )
    return handleResponse<ConversationListResponse>(response)
  },

  async get(id: string): Promise<ConversationResponse> {
    const response = await fetch(`${API_BASE}/conversations/${id}`, withAuth())
    return handleResponse<ConversationResponse>(response)
  },

  async create(data: {
    scope_type?: string
    scope_id?: string
    module?: string
    title?: string
    session_id?: string
  }): Promise<ConversationResponse> {
    const response = await fetch(
      `${API_BASE}/conversations`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<ConversationResponse>(response)
  },

  async update(
    id: string,
    data: { title?: string; status?: string }
  ): Promise<ConversationResponse> {
    const response = await fetch(
      `${API_BASE}/conversations/${id}`,
      withAuth({
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<ConversationResponse>(response)
  },

  async delete(id: string): Promise<void> {
    await fetch(
      `${API_BASE}/conversations/${id}`,
      withAuth({ method: 'DELETE' })
    )
  },

  async getMessages(
    id: string,
    params?: { limit?: number; before_seq?: number }
  ): Promise<MessageListResponse> {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.append('limit', String(params.limit))
    if (params?.before_seq)
      searchParams.append('before_seq', String(params.before_seq))
    const response = await fetch(
      `${API_BASE}/conversations/${id}/messages?${searchParams}`,
      withAuth()
    )
    return handleResponse<MessageListResponse>(response)
  },

  async addFeedback(
    conversationId: string,
    messageId: string,
    data: { rating: string; content?: string }
  ): Promise<FeedbackResponse> {
    const response = await fetch(
      `${API_BASE}/conversations/${conversationId}/messages/${messageId}/feedback`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<FeedbackResponse>(response)
  },

  async branch(
    conversationId: string,
    messageId: string
  ): Promise<BranchResponse> {
    const response = await fetch(
      `${API_BASE}/conversations/${conversationId}/branch`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message_id: messageId }),
      })
    )
    return handleResponse<BranchResponse>(response)
  },

  async getSiblings(
    conversationId: string,
    messageId: string
  ): Promise<SiblingResponse> {
    const response = await fetch(
      `${API_BASE}/conversations/${conversationId}/messages/${messageId}/siblings`,
      withAuth()
    )
    return handleResponse<SiblingResponse>(response)
  },
}
