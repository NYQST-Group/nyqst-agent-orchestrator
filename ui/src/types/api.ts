/**
 * API Types matching the FastAPI Pydantic schemas
 */

// Artifact types
export interface Artifact {
  sha256: string
  media_type: string
  size_bytes: number
  storage_uri: string
  original_filename?: string
  reference_count: number
  created_at: string
}

export interface ArtifactUploadResponse {
  sha256: string
  media_type: string
  size_bytes: number
  deduplicated: boolean
}

// Manifest types
export interface ManifestEntry {
  path: string
  ref_type: 'artifact' | 'manifest'
  ref_sha256: string
  media_type?: string
  size_bytes?: number
  metadata?: Record<string, unknown>
}

export interface Manifest {
  sha256: string
  parent_sha256?: string
  created_by?: string
  message?: string
  entry_count: number
  total_size_bytes: number
  created_at: string
}

export interface ManifestCreate {
  parent_sha256?: string
  created_by?: string
  message?: string
  entries: ManifestEntry[]
}

export interface ManifestDiff {
  added: ManifestEntry[]
  removed: ManifestEntry[]
  modified: Array<{
    path: string
    old: ManifestEntry
    new: ManifestEntry
  }>
}

// Pointer types
export interface Pointer {
  id: string
  namespace: string
  name: string
  head_sha256?: string
  version: number
  created_at: string
  updated_at: string
}

export interface PointerCreate {
  namespace: string
  name: string
  initial_sha256?: string
}

export interface PointerAdvance {
  new_sha256: string
  expected_version?: number
  reason?: string
  changed_by?: string
}

export interface PointerHistory {
  id: string
  pointer_id: string
  from_sha256?: string
  to_sha256: string
  version: number
  reason?: string
  changed_by?: string
  changed_at: string
}

// Run types
export type RunStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'

export type RunType =
  | 'ingest'
  | 'analysis'
  | 'research'
  | 'transform'
  | 'export'
  | 'custom'

export interface Run {
  id: string
  run_type: RunType
  status: RunStatus
  config: Record<string, unknown>
  input_manifest_sha256?: string
  output_manifest_sha256?: string
  checkpoint_data?: Record<string, unknown>
  error_message?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface RunCreate {
  run_type: RunType
  config?: Record<string, unknown>
  input_manifest_sha256?: string
}

// Run Event types
export type RunEventType =
  | 'step_start'
  | 'step_complete'
  | 'tool_call'
  | 'llm_call'
  | 'checkpoint'
  | 'error'
  | 'artifact_created'
  | 'custom'

export interface RunEvent {
  id: number
  run_id: string
  event_type: RunEventType
  payload: Record<string, unknown>
  timestamp: string
  duration_ms?: number
  sequence_num: number
}

// SSE Event types
export interface SSERunEvent {
  id: number
  run_id: string
  event_type: RunEventType
  payload: Record<string, unknown>
  timestamp: string
  duration_ms?: number
  sequence_num: number
}

export interface SSEActivityEvent {
  runs: Array<{
    type: 'run'
    run_id: string
    run_type: RunType
    status: RunStatus
    created_at: string
  }>
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
