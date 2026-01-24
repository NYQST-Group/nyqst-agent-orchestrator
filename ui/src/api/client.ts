/**
 * API Client for Intelli platform
 */

import type {
  Artifact,
  ArtifactUploadResponse,
  Manifest,
  ManifestCreate,
  ManifestCreateResponse,
  ManifestDiff,
  ManifestEntry,
  Pointer,
  PointerAdvance,
  PointerAdvanceResponse,
  PointerCreate,
  PointerHistoryEntry,
  RagAskRequest,
  RagAskResponse,
  RagIndexRequest,
  RagIndexResponse,
  Run,
  RunCreate,
  RunEvent,
  RunEventListResponse,
  RunListResponse,
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
  async upload(file: File, mediaType?: string): Promise<ArtifactUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (mediaType) {
      formData.append('media_type', mediaType)
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

  async list(limit = 20, offset = 0): Promise<Artifact[]> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    const response = await fetch(`${API_BASE}/artifacts?${params}`, withAuth())
    return handleResponse<Artifact[]>(response)
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
  async create(data: ManifestCreate): Promise<ManifestCreateResponse> {
    const response = await fetch(
      `${API_BASE}/manifests`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<ManifestCreateResponse>(response)
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

  async advance(id: string, data: PointerAdvance): Promise<PointerAdvanceResponse> {
    const response = await fetch(
      `${API_BASE}/pointers/${id}/advance`,
      withAuth({
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<PointerAdvanceResponse>(response)
  },

  async getHistory(id: string): Promise<PointerHistoryEntry[]> {
    const response = await fetch(`${API_BASE}/pointers/${id}/history`, withAuth())
    return handleResponse<PointerHistoryEntry[]>(response)
  },

  async resolve(namespace: string, name: string): Promise<{ manifest_sha256: string | null }> {
    const response = await fetch(
      `${API_BASE}/pointers/${namespace}/${name}/resolve`,
      withAuth()
    )
    return handleResponse<{ manifest_sha256: string | null }>(response)
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
    limit = 20,
    offset = 0
  ): Promise<RunListResponse> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (status) params.append('status', status)
    if (runType) params.append('run_type', runType)

    const response = await fetch(`${API_BASE}/runs?${params}`, withAuth())
    return handleResponse<RunListResponse>(response)
  },

  async start(id: string): Promise<Run> {
    const response = await fetch(
      `${API_BASE}/runs/${id}/start`,
      withAuth({ method: 'POST' })
    )
    return handleResponse<Run>(response)
  },

  async complete(id: string, outputManifestSha256?: string): Promise<Run> {
    const url = outputManifestSha256
      ? `${API_BASE}/runs/${id}/complete?output_manifest_sha256=${encodeURIComponent(outputManifestSha256)}`
      : `${API_BASE}/runs/${id}/complete`
    const response = await fetch(url, withAuth({ method: 'POST' }))
    return handleResponse<Run>(response)
  },

  async fail(id: string, errorMessage: string): Promise<Run> {
    const response = await fetch(
      `${API_BASE}/runs/${id}/fail`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: { type: 'error', message: errorMessage } }),
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
    const data = await handleResponse<RunEventListResponse>(response)
    return data.items
  },
}

// RAG API
export const ragApi = {
  async index(data: RagIndexRequest): Promise<RagIndexResponse> {
    const response = await fetch(
      `${API_BASE}/rag/index`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<RagIndexResponse>(response)
  },

  async ask(data: RagAskRequest): Promise<RagAskResponse> {
    const response = await fetch(
      `${API_BASE}/rag/ask`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    )
    return handleResponse<RagAskResponse>(response)
  },
}

export { ApiError }
