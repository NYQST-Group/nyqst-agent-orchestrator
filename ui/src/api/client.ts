/**
 * API Client for Intelli platform
 */

import type {
  Artifact,
  ArtifactUploadResponse,
  Manifest,
  ManifestCreate,
  ManifestDiff,
  ManifestEntry,
  Pointer,
  PointerAdvance,
  PointerCreate,
  PointerHistory,
  Run,
  RunCreate,
  RunEvent,
  PaginatedResponse,
} from '@/types/api'
import { getAuthHeaders } from '@/stores/auth-store'

const API_BASE = '/api/v1'

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

/**
 * Create fetch options with auth headers
 */
function withAuth(options: RequestInit = {}): RequestInit {
  return {
    ...options,
    headers: {
      ...options.headers,
      ...getAuthHeaders(),
    },
  }
}

// Artifacts API
export const artifactsApi = {
  async upload(file: File, filename?: string): Promise<ArtifactUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (filename) {
      formData.append('filename', filename)
    }

    const response = await fetch(
      `${API_BASE}/artifacts`,
      withAuth({ method: 'POST', body: formData })
    )
    return handleResponse<ArtifactUploadResponse>(response)
  },

  async get(sha256: string): Promise<Artifact> {
    const response = await fetch(`${API_BASE}/artifacts/${sha256}`, withAuth())
    return handleResponse<Artifact>(response)
  },

  async list(page = 1, size = 20): Promise<PaginatedResponse<Artifact>> {
    const response = await fetch(
      `${API_BASE}/artifacts?page=${page}&size=${size}`,
      withAuth()
    )
    return handleResponse<PaginatedResponse<Artifact>>(response)
  },

  async getContentUrl(sha256: string): Promise<{ url: string }> {
    const response = await fetch(`${API_BASE}/artifacts/${sha256}/url`, withAuth())
    return handleResponse<{ url: string }>(response)
  },

  async delete(sha256: string): Promise<void> {
    const response = await fetch(
      `${API_BASE}/artifacts/${sha256}`,
      withAuth({ method: 'DELETE' })
    )
    if (!response.ok) {
      throw new ApiError(response.status, response.statusText)
    }
  },
}

// Manifests API
export const manifestsApi = {
  async create(data: ManifestCreate): Promise<Manifest> {
    const response = await fetch(
      `${API_BASE}/manifests`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<Manifest>(response)
  },

  async get(sha256: string): Promise<Manifest> {
    const response = await fetch(`${API_BASE}/manifests/${sha256}`, withAuth())
    return handleResponse<Manifest>(response)
  },

  async getEntries(sha256: string): Promise<ManifestEntry[]> {
    const response = await fetch(`${API_BASE}/manifests/${sha256}/entries`, withAuth())
    return handleResponse<ManifestEntry[]>(response)
  },

  async getHistory(sha256: string): Promise<Manifest[]> {
    const response = await fetch(`${API_BASE}/manifests/${sha256}/history`, withAuth())
    return handleResponse<Manifest[]>(response)
  },

  async diff(oldSha256: string, newSha256: string): Promise<ManifestDiff> {
    const response = await fetch(
      `${API_BASE}/manifests/${oldSha256}/diff/${newSha256}`,
      withAuth()
    )
    return handleResponse<ManifestDiff>(response)
  },
}

// Pointers API
export const pointersApi = {
  async create(data: PointerCreate): Promise<Pointer> {
    const response = await fetch(
      `${API_BASE}/pointers`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<Pointer>(response)
  },

  async get(namespace: string, name: string): Promise<Pointer> {
    const response = await fetch(`${API_BASE}/pointers/${namespace}/${name}`, withAuth())
    return handleResponse<Pointer>(response)
  },

  async list(namespace?: string): Promise<Pointer[]> {
    const url = namespace
      ? `${API_BASE}/pointers?namespace=${namespace}`
      : `${API_BASE}/pointers`
    const response = await fetch(url, withAuth())
    return handleResponse<Pointer[]>(response)
  },

  async advance(id: string, data: PointerAdvance): Promise<Pointer> {
    const response = await fetch(
      `${API_BASE}/pointers/${id}/advance`,
      withAuth({
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<Pointer>(response)
  },

  async getHistory(id: string): Promise<PointerHistory[]> {
    const response = await fetch(`${API_BASE}/pointers/${id}/history`, withAuth())
    return handleResponse<PointerHistory[]>(response)
  },

  async resolve(namespace: string, name: string): Promise<Manifest> {
    const response = await fetch(
      `${API_BASE}/pointers/${namespace}/${name}/resolve`,
      withAuth()
    )
    return handleResponse<Manifest>(response)
  },
}

// Runs API
export const runsApi = {
  async create(data: RunCreate): Promise<Run> {
    const response = await fetch(
      `${API_BASE}/runs`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<Run>(response)
  },

  async get(id: string): Promise<Run> {
    const response = await fetch(`${API_BASE}/runs/${id}`, withAuth())
    return handleResponse<Run>(response)
  },

  async list(
    status?: string,
    runType?: string,
    page = 1,
    size = 20
  ): Promise<PaginatedResponse<Run>> {
    const params = new URLSearchParams({ page: String(page), size: String(size) })
    if (status) params.append('status', status)
    if (runType) params.append('run_type', runType)

    const response = await fetch(`${API_BASE}/runs?${params}`, withAuth())
    return handleResponse<PaginatedResponse<Run>>(response)
  },

  async start(id: string): Promise<Run> {
    const response = await fetch(
      `${API_BASE}/runs/${id}/start`,
      withAuth({ method: 'POST' })
    )
    return handleResponse<Run>(response)
  },

  async complete(id: string, outputManifestSha256?: string): Promise<Run> {
    const response = await fetch(
      `${API_BASE}/runs/${id}/complete`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ output_manifest_sha256: outputManifestSha256 }),
      })
    )
    return handleResponse<Run>(response)
  },

  async fail(id: string, errorMessage: string): Promise<Run> {
    const response = await fetch(
      `${API_BASE}/runs/${id}/fail`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error_message: errorMessage }),
      })
    )
    return handleResponse<Run>(response)
  },

  async getEvents(
    id: string,
    sinceSequence?: number,
    limit?: number
  ): Promise<RunEvent[]> {
    const params = new URLSearchParams()
    if (sinceSequence !== undefined) {
      params.append('since_sequence', String(sinceSequence))
    }
    if (limit !== undefined) {
      params.append('limit', String(limit))
    }

    const response = await fetch(`${API_BASE}/runs/${id}/events?${params}`, withAuth())
    return handleResponse<RunEvent[]>(response)
  },
}

export { ApiError }
