/**
 * Mock API layer for demo mode.
 * Returns static fixtures instead of hitting the backend.
 */

import type {
  Artifact,
  ArtifactUploadResponse,
  Manifest,
  ManifestCreateResponse,
  ManifestDiff,
  ManifestEntry,
  Pointer,
  PointerAdvanceResponse,
  PointerHistoryEntry,
  RagAskResponse,
  RagIndexResponse,
  Run,
  RunEvent,
  RunListResponse,
} from '@/types/api'

import {
  MOCK_POINTERS,
  MOCK_ARTIFACTS,
  MOCK_RUNS,
  MOCK_RUN_LIST,
  MOCK_RAG_INDEX,
  MOCK_RAG_ASK,
} from './fixtures'

const delay = (ms = 200) => new Promise((r) => setTimeout(r, ms))

export const mockArtifactsApi = {
  async upload(): Promise<ArtifactUploadResponse> {
    await delay()
    return { sha256: 'mock-sha256', size_bytes: 1000, is_duplicate: false }
  },
  async get(): Promise<Artifact> {
    await delay()
    return MOCK_ARTIFACTS[0]
  },
  async list(): Promise<Artifact[]> {
    await delay()
    return MOCK_ARTIFACTS
  },
  async getContentUrl(): Promise<{ url: string }> {
    await delay()
    return { url: '#demo-mode' }
  },
  async delete(): Promise<void> {
    await delay()
  },
}

export const mockManifestsApi = {
  async create(): Promise<ManifestCreateResponse> {
    await delay()
    return { sha256: 'mock-manifest', entry_count: 2, total_size_bytes: 5000, is_duplicate: false }
  },
  async get(): Promise<Manifest> {
    await delay()
    return {
      sha256: 'abc123def456',
      tree: { entries: [], metadata: null },
      entry_count: 2,
      total_size_bytes: 257_400,
      created_at: new Date().toISOString(),
    }
  },
  async getEntries(): Promise<ManifestEntry[]> {
    await delay()
    return MOCK_ARTIFACTS.map((a) => ({
      path: a.filename || a.sha256,
      artifact_sha256: a.sha256,
    }))
  },
  async getHistory(): Promise<Manifest[]> {
    await delay()
    return []
  },
  async diff(): Promise<ManifestDiff> {
    await delay()
    return { old_sha256: '', new_sha256: '', added: [], removed: [], modified: [] }
  },
}

export const mockPointersApi = {
  async create(): Promise<Pointer> {
    await delay()
    return MOCK_POINTERS[0]
  },
  async get(): Promise<Pointer> {
    await delay()
    return MOCK_POINTERS[0]
  },
  async list(namespace?: string): Promise<Pointer[]> {
    await delay()
    if (namespace) {
      return MOCK_POINTERS.filter((p) => p.namespace === namespace)
    }
    return MOCK_POINTERS
  },
  async advance(): Promise<PointerAdvanceResponse> {
    await delay()
    return { success: true, new_sha256: 'mock-new', conflict: false }
  },
  async getHistory(): Promise<PointerHistoryEntry[]> {
    await delay()
    return []
  },
  async resolve(): Promise<{ manifest_sha256: string | null }> {
    await delay()
    return { manifest_sha256: 'abc123def456' }
  },
}

export const mockRunsApi = {
  async create(): Promise<Run> {
    await delay()
    return MOCK_RUNS[0]
  },
  async get(): Promise<Run> {
    await delay()
    return MOCK_RUNS[0]
  },
  async list(): Promise<RunListResponse> {
    await delay()
    return MOCK_RUN_LIST
  },
  async start(): Promise<Run> {
    await delay()
    return { ...MOCK_RUNS[0], status: 'running' }
  },
  async complete(): Promise<Run> {
    await delay()
    return MOCK_RUNS[0]
  },
  async fail(): Promise<Run> {
    await delay()
    return { ...MOCK_RUNS[0], status: 'failed' }
  },
  async getEvents(): Promise<RunEvent[]> {
    await delay()
    return []
  },
}

export const mockRagApi = {
  async index(): Promise<RagIndexResponse> {
    await delay(500)
    return MOCK_RAG_INDEX
  },
  async ask(): Promise<RagAskResponse> {
    await delay(800)
    return MOCK_RAG_ASK
  },
}
