/**
 * Auth API client
 */

import { getAuthHeaders } from '@/stores/auth-store'

const API_BASE = '/api/v1'

interface LoginRequest {
  email: string
  password: string
  tenant_slug: string
}

interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  tenant_id: string
  user_id: string
}

interface CurrentUser {
  user_id: string | null
  tenant_id: string
  tenant_name: string
  role: string | null
  scopes: string[]
  api_key_id: string | null
}

interface APIKey {
  id: string
  name: string
  key_prefix: string
  scopes: string[]
  expires_at: string | null
  rate_limit_rpm: number
  is_active: boolean
  last_used_at: string | null
  use_count: number
  created_at: string
}

interface APIKeyCreated extends APIKey {
  full_key: string
}

interface CreateAPIKeyRequest {
  name: string
  scopes: string[]
  expires_in_days?: number
  rate_limit_rpm?: number
  allowed_ips?: string[]
}

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: unknown
    try {
      body = await response.json()
    } catch {
      body = await response.text()
    }
    throw new ApiError(response.status, response.statusText, body)
  }
  return response.json()
}

export const authApi = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse<LoginResponse>(response)
  },

  async getCurrentUser(): Promise<CurrentUser> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    })
    return handleResponse<CurrentUser>(response)
  },

  async listAPIKeys(): Promise<APIKey[]> {
    const response = await fetch(`${API_BASE}/auth/keys`, {
      headers: getAuthHeaders(),
    })
    return handleResponse<APIKey[]>(response)
  },

  async createAPIKey(data: CreateAPIKeyRequest): Promise<APIKeyCreated> {
    const response = await fetch(`${API_BASE}/auth/keys`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(data),
    })
    return handleResponse<APIKeyCreated>(response)
  },

  async revokeAPIKey(keyId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/auth/keys/${keyId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      throw new ApiError(response.status, response.statusText)
    }
  },
}

export { ApiError }
export type { LoginRequest, LoginResponse, CurrentUser, APIKey, APIKeyCreated, CreateAPIKeyRequest }
