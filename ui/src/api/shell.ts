import { getAuthHeaders } from '@/stores/auth-store'
import type { OpsSummary, RightRailPayload, ShellContext } from '@/types/shell'

const API_BASE = '/api/v1'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: unknown
    try {
      body = await response.json()
    } catch {
      body = await response.text()
    }
    throw new Error(`API Error: ${response.status} ${response.statusText} ${JSON.stringify(body)}`)
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

export const shellApi = {
  async getContext(): Promise<ShellContext> {
    const response = await fetch(`${API_BASE}/shell/context`, withAuth())
    return handleResponse<ShellContext>(response)
  },

  async getOpsSummary(): Promise<OpsSummary> {
    const response = await fetch(`${API_BASE}/ops/summary`, withAuth())
    return handleResponse<OpsSummary>(response)
  },

  async getRightRail(module: string): Promise<RightRailPayload> {
    const params = new URLSearchParams({ module })
    const response = await fetch(`${API_BASE}/shell/right-rail?${params}`, withAuth())
    return handleResponse<RightRailPayload>(response)
  },
}
