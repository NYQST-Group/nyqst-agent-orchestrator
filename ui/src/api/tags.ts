/**
 * API client for tags.
 */

import type { TagResponse, TagListResponse } from '@/types/tags'
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

export const tagsApi = {
  async add(data: {
    entity_type: string
    entity_id: string
    namespace: string
    key: string
    value: string
    source?: string
    confidence?: number
  }): Promise<TagResponse> {
    const response = await fetch(
      `${API_BASE}/tags`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<TagResponse>(response)
  },

  async remove(id: string): Promise<void> {
    await fetch(`${API_BASE}/tags/${id}`, withAuth({ method: 'DELETE' }))
  },

  async list(params?: {
    entity_type?: string
    entity_id?: string
    namespace?: string
    key?: string
    value?: string
    limit?: number
    offset?: number
  }): Promise<TagListResponse> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) searchParams.append(k, String(v))
      })
    }
    const response = await fetch(`${API_BASE}/tags?${searchParams}`, withAuth())
    return handleResponse<TagListResponse>(response)
  },

  async search(params: {
    namespace?: string
    key?: string
    value?: string
    limit?: number
  }): Promise<Array<{ entity_type: string; entity_id: string; tags: TagResponse[] }>> {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined) searchParams.append(k, String(v))
    })
    const response = await fetch(`${API_BASE}/tags/search?${searchParams}`, withAuth())
    return handleResponse(response)
  },
}
