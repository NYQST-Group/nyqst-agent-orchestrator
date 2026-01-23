/**
 * Knowledge System types
 * KnowledgeBases, Retrieval Profiles, Index Snapshots
 */

import type { UUID, Timestamp, TenantScopedEntity, ProjectScopedEntity, ContentHash, SchemaRef, SemanticVersion } from './core';

// ============================================================================
// Knowledge Bases (Section 3.6)
// ============================================================================

export type KnowledgeBaseStatus = 'building' | 'ready' | 'stale' | 'error';

export interface KnowledgeBase extends TenantScopedEntity {
  name: string;
  description?: string;
  projectId?: UUID;
  status: KnowledgeBaseStatus;
  /** Source corpus/bundle versions */
  sources: KnowledgeBaseSource[];
  /** Indexing configuration */
  indexingConfig: IndexingConfig;
  /** Current index head pointer */
  indexHeadPointerId?: UUID;
  /** Available retrieval profiles */
  retrievalProfiles: RetrievalProfile[];
  /** Evaluation suite references */
  evaluationSuiteIds: UUID[];
  metadata: Record<string, unknown>;
}

export interface KnowledgeBaseSource {
  type: 'corpus' | 'bundle' | 'manifest';
  id: UUID;
  manifestId: UUID;
  inclusionRules?: InclusionRule[];
}

export interface InclusionRule {
  type: 'include' | 'exclude';
  pattern: string;
  field: 'path' | 'logicalType' | 'metadata';
}

export interface IndexingConfig {
  /** Chunking strategy */
  chunking: ChunkingConfig;
  /** Embedding model configuration */
  embedding: EmbeddingConfig;
  /** Sparse index configuration (BM25, etc.) */
  sparse?: SparseIndexConfig;
  /** Graph extraction configuration */
  graph?: GraphIndexConfig;
  /** Reranker configuration */
  reranker?: RerankerConfig;
}

export interface ChunkingConfig {
  strategy: 'fixed' | 'semantic' | 'document_structure' | 'sliding_window';
  maxTokens: number;
  overlapTokens: number;
  respectBoundaries: boolean;
}

export interface EmbeddingConfig {
  model: string;
  modelVersion: string;
  dimensions: number;
  batchSize: number;
}

export interface SparseIndexConfig {
  analyzer: 'standard' | 'english' | 'custom';
  customAnalyzerConfig?: Record<string, unknown>;
}

export interface GraphIndexConfig {
  extractEntities: boolean;
  extractRelations: boolean;
  entityTypes?: string[];
  relationTypes?: string[];
}

export interface RerankerConfig {
  model: string;
  modelVersion: string;
  topK: number;
}

// ============================================================================
// Index Snapshots
// ============================================================================

export interface IndexSnapshot extends TenantScopedEntity {
  knowledgeBaseId: UUID;
  /** Source corpus/manifest version this index was built from */
  sourceManifestId: UUID;
  /** Index artifacts (chunks, embeddings, sparse postings, etc.) */
  indexArtifacts: IndexArtifact[];
  /** Tool and model versions used */
  buildInfo: IndexBuildInfo;
  /** Build timing */
  buildStartedAt: Timestamp;
  buildCompletedAt?: Timestamp;
  /** Statistics */
  stats: IndexStats;
  metadata: Record<string, unknown>;
}

export interface IndexArtifact {
  type: 'chunks' | 'embeddings' | 'sparse_postings' | 'metadata_table' | 'graph_extract';
  artifactId: UUID;
}

export interface IndexBuildInfo {
  chunkingVersion: string;
  embeddingModel: string;
  embeddingModelVersion: string;
  sparseAnalyzer?: string;
  graphExtractorVersion?: string;
  configHash: ContentHash;
}

export interface IndexStats {
  totalDocuments: number;
  totalChunks: number;
  totalTokens: number;
  avgChunkSize: number;
  buildDurationMs: number;
}

// ============================================================================
// Retrieval Profiles
// ============================================================================

export type RetrievalProfileType = 'fast_skim' | 'legal_citations' | 'strict_evidence' | 'custom';

export interface RetrievalProfile {
  id: string;
  name: string;
  type: RetrievalProfileType;
  description?: string;
  config: RetrievalConfig;
}

export interface RetrievalConfig {
  /** Vector search parameters */
  vector: VectorSearchConfig;
  /** Sparse search parameters (hybrid search) */
  sparse?: SparseSearchConfig;
  /** Filtering rules */
  filters?: RetrievalFilter[];
  /** Reranking configuration */
  rerank?: RerankConfig;
  /** Post-processing */
  postProcess?: PostProcessConfig;
}

export interface VectorSearchConfig {
  topK: number;
  similarityThreshold?: number;
  efSearch?: number; // HNSW parameter
}

export interface SparseSearchConfig {
  enabled: boolean;
  topK: number;
  weight: number; // Hybrid weight (0-1, where 0 is vector only, 1 is sparse only)
}

export interface RetrievalFilter {
  field: string;
  operator: 'eq' | 'ne' | 'in' | 'nin' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains';
  value: unknown;
}

export interface RerankConfig {
  enabled: boolean;
  model: string;
  topK: number;
}

export interface PostProcessConfig {
  deduplication: boolean;
  maxTokens?: number;
  includeMetadata: boolean;
  includeScores: boolean;
}

// ============================================================================
// Retrieval Results
// ============================================================================

export interface RetrievalQuery {
  query: string;
  profileId: string;
  filters?: RetrievalFilter[];
  topK?: number;
  includeMetadata?: boolean;
}

export interface RetrievalResult {
  queryId: UUID;
  knowledgeBaseId: UUID;
  profileId: string;
  query: string;
  results: RetrievalResultItem[];
  totalResults: number;
  searchDurationMs: number;
  metadata: Record<string, unknown>;
}

export interface RetrievalResultItem {
  chunkId: UUID;
  artifactId: UUID;
  content: string;
  /** Score from vector search */
  vectorScore?: number;
  /** Score from sparse search */
  sparseScore?: number;
  /** Combined/reranked score */
  finalScore: number;
  /** Evidence span information */
  evidenceSpan?: EvidenceSpanRef;
  /** Chunk metadata */
  metadata: Record<string, unknown>;
}

export interface EvidenceSpanRef {
  documentId: UUID;
  pageNumber?: number;
  blockId?: string;
  startOffset: number;
  endOffset: number;
}

// ============================================================================
// Data Assets (Section 18.1)
// ============================================================================

export type DataAssetType = 'dataset' | 'database' | 'graph' | 'index_snapshot' | 'model_spec' | 'skill_pack';

export interface DataAsset extends TenantScopedEntity {
  type: DataAssetType;
  name: string;
  description?: string;
  projectId?: UUID;
  /** Current version manifest */
  currentManifestId: UUID;
  /** Version history */
  versions: DataAssetVersion[];
  /** Access policy */
  policyId?: UUID;
  metadata: Record<string, unknown>;
}

export interface DataAssetVersion {
  version: number;
  manifestId: UUID;
  createdAt: Timestamp;
  createdBy: UUID;
  changelog?: string;
}

// ============================================================================
// Model Specs (Section 17)
// ============================================================================

export interface ModelSpec extends TenantScopedEntity {
  name: string;
  description?: string;
  version: SemanticVersion;
  /** Entity/table definitions */
  entities: ModelEntity[];
  /** Relationships between entities */
  relationships: ModelRelationship[];
  /** Constraints and validations */
  constraints: ModelConstraint[];
  /** Lineage to evidence/sources */
  lineage: ModelLineage[];
  /** Schema registry reference */
  schemaRef?: SchemaRef;
  metadata: Record<string, unknown>;
}

export interface ModelEntity {
  name: string;
  description?: string;
  fields: ModelField[];
  primaryKey: string[];
  indexes?: ModelIndex[];
}

export interface ModelField {
  name: string;
  type: ModelFieldType;
  nullable: boolean;
  description?: string;
  defaultValue?: unknown;
  validation?: FieldValidation;
}

export type ModelFieldType =
  | 'string'
  | 'integer'
  | 'float'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'uuid'
  | 'json'
  | 'array'
  | 'enum';

export interface FieldValidation {
  pattern?: string;
  minLength?: number;
  maxLength?: number;
  minimum?: number;
  maximum?: number;
  enumValues?: string[];
}

export interface ModelIndex {
  name: string;
  fields: string[];
  unique: boolean;
}

export interface ModelRelationship {
  name: string;
  fromEntity: string;
  fromField: string;
  toEntity: string;
  toField: string;
  cardinality: 'one_to_one' | 'one_to_many' | 'many_to_many';
}

export interface ModelConstraint {
  name: string;
  type: 'unique' | 'check' | 'foreign_key';
  definition: string;
}

export interface ModelLineage {
  entityName: string;
  fieldName?: string;
  sourceType: 'corpus' | 'artifact' | 'claim';
  sourceId: UUID;
  evidenceSpan?: EvidenceSpanRef;
}

// ============================================================================
// Skill Packs (Section 19)
// ============================================================================

export interface SkillPack extends TenantScopedEntity {
  name: string;
  description?: string;
  version: SemanticVersion;
  /** Toolchain definitions */
  tools: SkillPackTool[];
  /** Prompt assets */
  prompts: PromptAsset[];
  /** Retrieval profile bindings */
  retrievalBindings: RetrievalBinding[];
  /** Evaluation suite */
  evaluationSuiteId?: UUID;
  /** Policy template requirements */
  policyRequirements?: PolicyRequirement[];
  metadata: Record<string, unknown>;
}

import type { PromptAsset } from './core';

export interface SkillPackTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  outputSchema?: Record<string, unknown>;
  implementation: 'mcp' | 'http' | 'builtin';
  endpoint?: string;
}

export interface RetrievalBinding {
  profileId: string;
  knowledgeBaseId: UUID;
  purpose: string;
}

export interface PolicyRequirement {
  type: 'governance_level' | 'approval_required' | 'audit_logging';
  value: unknown;
}
