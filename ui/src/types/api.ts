/**
 * API Types matching the FastAPI Pydantic schemas
 */

// Artifact types
export interface Artifact {
  sha256: string
  media_type: string
  size_bytes: number
  filename?: string | null
  storage_uri: string
  storage_class: string
  reference_count: number
  created_at: string
  created_by?: string | null
}

export interface ArtifactUploadResponse {
  sha256: string
  size_bytes: number
  is_duplicate: boolean
  content_url?: string | null
}

// Manifest types
export interface ManifestEntry {
  path: string
  artifact_sha256: string
  metadata?: Record<string, unknown> | null
}

export interface ManifestTree {
  entries: ManifestEntry[]
  metadata?: Record<string, unknown> | null
}

export interface Manifest {
  sha256: string
  tree: ManifestTree
  parent_sha256?: string
  message?: string
  entry_count: number
  total_size_bytes: number
  created_at: string
  created_by?: string | null
}

export interface ManifestCreate {
  entries: ManifestEntry[]
  parent_sha256?: string | null
  message?: string | null
  metadata?: Record<string, unknown> | null
}

export interface ManifestCreateResponse {
  sha256: string
  entry_count: number
  total_size_bytes: number
  is_duplicate: boolean
}

export interface ManifestDiff {
  old_sha256: string
  new_sha256: string
  added: ManifestEntry[]
  removed: ManifestEntry[]
  modified: Array<{
    path: string
    old: ManifestEntry
    new: ManifestEntry
  }>
}

// Pointer types
export type PointerType = 'bundle' | 'corpus' | 'snapshot'

export interface Pointer {
  id: string
  namespace: string
  name: string
  pointer_type: PointerType
  manifest_sha256?: string | null
  description?: string | null
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
  created_by?: string | null
}

export interface PointerCreate {
  namespace?: string
  name: string
  pointer_type?: PointerType
  manifest_sha256?: string | null
  description?: string | null
  metadata?: Record<string, unknown> | null
}

export interface PointerAdvance {
  manifest_sha256: string
  expected_sha256?: string | null
  reason?: string | null
}

export interface PointerAdvanceResponse {
  success: boolean
  old_sha256?: string | null
  new_sha256: string
  conflict: boolean
}

export interface PointerHistoryEntry {
  id: string
  old_sha256?: string | null
  new_sha256?: string | null
  operation: string
  changed_by?: string | null
  changed_at: string
  reason?: string | null
}

// Run types
export type RunStatus =
  | 'pending'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface Run {
  id: string
  run_type: string
  name?: string | null
  status: RunStatus
  started_at?: string | null
  completed_at?: string | null
  input_manifest_sha256?: string | null
  output_manifest_sha256?: string | null
  config: Record<string, unknown>
  result?: Record<string, unknown> | null
  error?: Record<string, unknown> | null
  token_usage: Record<string, unknown>
  cost_cents: number
  created_at: string
  created_by?: string | null
  project_id?: string | null
  session_id?: string | null
  parent_run_id?: string | null
}

export interface RunCreate {
  run_type: string
  name?: string | null
  config?: Record<string, unknown>
  input_manifest_sha256?: string | null
  project_id?: string | null
  session_id?: string | null
  parent_run_id?: string | null
}

export interface RunListResponse {
  items: Run[]
  total: number
  limit: number
  offset: number
}

export interface RunEvent {
  id: number
  run_id: string
  event_type: string
  payload: Record<string, unknown>
  timestamp: string
  duration_ms?: number
  sequence_num: number
}

// SSE Event types
export interface SSERunEvent {
  id: number
  run_id: string
  event_type: string
  payload: Record<string, unknown>
  timestamp: string
  duration_ms?: number
  sequence_num: number
}

export interface SSEActivityEvent {
  runs: Array<{
    type: 'run'
    run_id: string
    run_type: string
    status: RunStatus
    created_at: string
  }>
}

export interface RunEventListResponse {
  items: RunEvent[]
  run_id: string
  total: number
}

// RAG (demo-grade)
export interface RagIndexRequest {
  pointer_id?: string
  manifest_sha256?: string
  force?: boolean
}

export interface RagIndexResponse {
  run_id: string
  manifest_sha256: string
  embedding_model: string
  artifacts_total: number
  artifacts_indexed: number
  artifacts_skipped: number
  chunks_created: number
}

export interface RagAskRequest {
  pointer_id?: string
  manifest_sha256?: string
  question: string
  top_k?: number
}

export interface RagSource {
  chunk_id: string
  score: number
  artifact_sha256: string
  path?: string | null
  chunk_index: number
  content: string
}

export interface RagAskResponse {
  run_id: string
  model: string
  answer: string
  sources: RagSource[]
}
