/**
 * API client for sessions.
 */

import type { SessionResponse, SessionListResponse, SessionCostBreakdown } from '@/types/sessions'
import { getAuthHeaders } from '@/stores/auth-store'

const API_BASE = '/api/v1'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

function withAuth(options: RequestInit = {}): RequestInit {
  return {
    ...options,
    headers: { ...options.headers, ...getAuthHeaders() },
  }
}

export const sessionsApi = {
  async create(data: {
    scope_type?: string
    scope_id?: string
    module?: string
    objective?: string
    idle_timeout_minutes?: number
  }): Promise<SessionResponse> {
    const response = await fetch(
      `${API_BASE}/sessions`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<SessionResponse>(response)
  },

  async list(params?: {
    status?: string
    limit?: number
    offset?: number
  }): Promise<SessionListResponse> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) searchParams.append(k, String(v))
      })
    }
    const response = await fetch(`${API_BASE}/sessions?${searchParams}`, withAuth())
    return handleResponse<SessionListResponse>(response)
  },

  async get(id: string): Promise<SessionResponse> {
    const response = await fetch(`${API_BASE}/sessions/${id}`, withAuth())
    return handleResponse<SessionResponse>(response)
  },

  async updateStatus(
    id: string,
    data: { status: string; close_reason?: string }
  ): Promise<SessionResponse> {
    const response = await fetch(
      `${API_BASE}/sessions/${id}`,
      withAuth({
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<SessionResponse>(response)
  },

  async getCost(id: string): Promise<SessionCostBreakdown> {
    const response = await fetch(`${API_BASE}/sessions/${id}/cost`, withAuth())
    return handleResponse<SessionCostBreakdown>(response)
  },
}
