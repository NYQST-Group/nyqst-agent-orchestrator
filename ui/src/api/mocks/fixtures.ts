import type {
  Artifact,
  Pointer,
  Run,
  RunListResponse,
  RagAskResponse,
  RagIndexResponse,
} from '@/types/api'

const now = new Date().toISOString()

export const MOCK_POINTERS: Pointer[] = [
  {
    id: 'ptr-demo-1',
    namespace: 'notebooks',
    name: 'Q4 Market Research',
    pointer_type: 'corpus',
    manifest_sha256: 'abc123def456',
    description: 'Quarterly market analysis documents',
    metadata: { doc_count: 12 },
    created_at: now,
    updated_at: now,
    created_by: 'demo-user',
  },
  {
    id: 'ptr-demo-2',
    namespace: 'notebooks',
    name: 'Client Due Diligence',
    pointer_type: 'corpus',
    manifest_sha256: 'def456abc789',
    description: 'KYC and compliance documents',
    metadata: { doc_count: 8 },
    created_at: now,
    updated_at: now,
    created_by: 'demo-user',
  },
  {
    id: 'ptr-demo-3',
    namespace: 'notebooks',
    name: 'Investment Thesis',
    pointer_type: 'bundle',
    manifest_sha256: null,
    description: 'Working notes on current thesis',
    metadata: {},
    created_at: now,
    updated_at: now,
    created_by: 'demo-user',
  },
]

export const MOCK_ARTIFACTS: Artifact[] = [
  {
    sha256: 'a1b2c3d4e5f6',
    media_type: 'application/pdf',
    size_bytes: 245_000,
    filename: 'market-overview-q4.pdf',
    storage_uri: 'local://artifacts/a1b2c3d4e5f6',
    storage_class: 'local',
    reference_count: 1,
    created_at: now,
    created_by: 'demo-user',
  },
  {
    sha256: 'b2c3d4e5f6a1',
    media_type: 'text/csv',
    size_bytes: 12_400,
    filename: 'revenue-data.csv',
    storage_uri: 'local://artifacts/b2c3d4e5f6a1',
    storage_class: 'local',
    reference_count: 2,
    created_at: now,
    created_by: 'demo-user',
  },
]

export const MOCK_RUNS: Run[] = [
  {
    id: 'run-demo-1',
    run_type: 'rag_index',
    name: 'Index Q4 Research',
    status: 'completed',
    started_at: now,
    completed_at: now,
    input_manifest_sha256: 'abc123def456',
    output_manifest_sha256: null,
    config: { embedding_model: 'text-embedding-3-small' },
    result: { chunks_created: 142 },
    error: null,
    token_usage: { total: 8500 },
    cost_cents: 0.12,
    created_at: now,
    created_by: 'demo-user',
  },
  {
    id: 'run-demo-2',
    run_type: 'rag_ask',
    name: 'Research query',
    status: 'completed',
    started_at: now,
    completed_at: now,
    input_manifest_sha256: 'abc123def456',
    output_manifest_sha256: null,
    config: { model: 'gpt-4o' },
    result: { answer_length: 450 },
    error: null,
    token_usage: { total: 3200 },
    cost_cents: 0.08,
    created_at: now,
    created_by: 'demo-user',
  },
]

export const MOCK_RUN_LIST: RunListResponse = {
  items: MOCK_RUNS,
  total: MOCK_RUNS.length,
  limit: 20,
  offset: 0,
}

export const MOCK_RAG_INDEX: RagIndexResponse = {
  run_id: 'run-demo-index',
  manifest_sha256: 'abc123def456',
  embedding_model: 'text-embedding-3-small',
  artifacts_total: 12,
  artifacts_indexed: 12,
  artifacts_skipped: 0,
  chunks_created: 142,
}

export const MOCK_RAG_ASK: RagAskResponse = {
  run_id: 'run-demo-ask',
  model: 'gpt-4o',
  answer:
    'Based on the Q4 market analysis, the sector showed 12% growth YoY with particular strength in the European market. Key drivers included regulatory tailwinds and increased institutional adoption.',
  sources: [
    {
      chunk_id: 'chunk-1',
      score: 0.92,
      artifact_sha256: 'a1b2c3d4e5f6',
      path: 'market-overview-q4.pdf',
      chunk_index: 3,
      content:
        'The European market demonstrated remarkable resilience in Q4, with 12% year-over-year growth driven by regulatory clarity...',
    },
    {
      chunk_id: 'chunk-2',
      score: 0.87,
      artifact_sha256: 'a1b2c3d4e5f6',
      path: 'market-overview-q4.pdf',
      chunk_index: 7,
      content:
        'Institutional adoption accelerated following the framework publication, with AUM increasing 23% across tracked funds...',
    },
  ],
}
