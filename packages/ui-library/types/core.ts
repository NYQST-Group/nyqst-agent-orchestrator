/**
 * Core domain types for the Agent-First Document Intelligence Platform
 * Based on the Reference Design v1.1 backbone objects
 */

// ============================================================================
// Base Types
// ============================================================================

/** UUID type alias for clarity */
export type UUID = string;

/** ISO 8601 timestamp string */
export type Timestamp = string;

/** Content-addressed hash (e.g., SHA-256) */
export type ContentHash = string;

/** Semantic version string */
export type SemanticVersion = `${number}.${number}.${number}`;

/** URI scheme for platform resources */
export type ResourceURI =
  | `project://${string}`
  | `bundle://${string}`
  | `corpus://${string}`
  | `run://${string}`
  | `artifact://${string}`
  | `claim://${string}`
  | `kb://${string}`
  | `thread://${string}`
  | `session://${string}`;

/** Base entity with common fields */
export interface BaseEntity {
  id: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

/** Entity with tenant scope */
export interface TenantScopedEntity extends BaseEntity {
  tenantId: UUID;
}

/** Entity with project scope */
export interface ProjectScopedEntity extends TenantScopedEntity {
  projectId: UUID;
}

// ============================================================================
// Identity & Tenancy (Section 3.1)
// ============================================================================

export type PrincipalType = 'user' | 'service' | 'agent';

export interface Principal extends TenantScopedEntity {
  type: PrincipalType;
  displayName: string;
  email?: string;
  avatarUrl?: string;
  metadata: Record<string, unknown>;
}

export interface Tenant extends BaseEntity {
  name: string;
  slug: string;
  dataResidency: string;
  billingStatus: 'active' | 'suspended' | 'trial';
  settings: TenantSettings;
}

export interface TenantSettings {
  retentionDays: number;
  allowedTools: string[];
  defaultGovernanceProfile: UUID | null;
  ssoEnabled: boolean;
  ssoProvider?: string;
}

export type PolicyEffect = 'allow' | 'deny';
export type PolicyScope = 'project' | 'corpus' | 'kb' | 'tool' | 'connector';

export interface AccessPolicy extends TenantScopedEntity {
  name: string;
  effect: PolicyEffect;
  scope: PolicyScope;
  scopeId?: UUID;
  principalIds: UUID[];
  actions: string[];
  conditions?: Record<string, unknown>;
}

// ============================================================================
// Work Coordination (Section 3.2)
// ============================================================================

export type ProjectStatus = 'active' | 'completed' | 'archived' | 'paused';

export interface Project extends TenantScopedEntity {
  name: string;
  description?: string;
  status: ProjectStatus;
  ownerId: UUID;
  defaultBundleId?: UUID;
  defaultCorpusId?: UUID;
  defaultKbId?: UUID;
  settings: ProjectSettings;
  metadata: Record<string, unknown>;
}

export interface ProjectSettings {
  governanceProfile?: UUID;
  allowedConnectors: UUID[];
  defaultRetrievalProfile?: string;
  autoPublish: boolean;
}

export type ObjectiveStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';
export type ObjectivePriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Objective extends ProjectScopedEntity {
  title: string;
  description?: string;
  status: ObjectiveStatus;
  priority: ObjectivePriority;
  assigneeId?: UUID;
  parentId?: UUID;
  dueDate?: Timestamp;
  linkedRunIds: UUID[];
  linkedArtifactIds: UUID[];
}

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface Task extends ProjectScopedEntity {
  objectiveId?: UUID;
  title: string;
  description?: string;
  status: TaskStatus;
  assigneeId?: UUID;
  dueDate?: Timestamp;
  externalRef?: ExternalReference;
}

export interface ExternalReference {
  provider: string;
  externalId: string;
  url?: string;
}

// ============================================================================
// Artifact Substrate (Section 3.3)
// ============================================================================

export type ArtifactLogicalType =
  | 'document'
  | 'table'
  | 'graph'
  | 'model'
  | 'image'
  | 'report'
  | 'evidence'
  | 'claim_set'
  | 'index_snapshot'
  | 'plan'
  | 'config'
  | 'other';

export type ArtifactMimeType =
  | 'application/pdf'
  | 'application/json'
  | 'application/x-parquet'
  | 'text/markdown'
  | 'text/html'
  | 'text/plain'
  | 'image/png'
  | 'image/jpeg'
  | 'application/octet-stream';

/**
 * Artifact - Immutable content-addressed object
 * Any file/object emitted (pdf/json/parquet/md/html/png)
 */
export interface Artifact extends TenantScopedEntity {
  /** Content hash for deduplication and verification */
  contentHash: ContentHash;
  /** Logical type for categorization */
  logicalType: ArtifactLogicalType;
  /** MIME type */
  mimeType: ArtifactMimeType;
  /** File size in bytes */
  sizeBytes: number;
  /** Original filename if applicable */
  filename?: string;
  /** Schema reference if structured */
  schemaRef?: SchemaRef;
  /** Run that created this artifact */
  createdByRunId?: UUID;
  /** Custom metadata */
  metadata: Record<string, unknown>;
  /** Storage location (internal) */
  storageKey: string;
}

export interface SchemaRef {
  schemaId: UUID;
  version: SemanticVersion;
}

export type ManifestKind =
  | 'bundle_snapshot'
  | 'corpus_version'
  | 'run_output'
  | 'kb_index_snapshot'
  | 'model_pack'
  | 'skill_pack'
  | 'xpkg';

/**
 * Manifest - Immutable tree of references
 * Used for bundles, corpus versions, run outputs, KB index snapshots
 */
export interface Manifest extends TenantScopedEntity {
  kind: ManifestKind;
  /** Human-readable description */
  description?: string;
  /** Version number within its pointer lineage */
  version: number;
  /** References to artifacts and nested manifests */
  entries: ManifestEntry[];
  /** How this manifest was captured/created */
  captureMethod?: CaptureMethod;
  /** Producing run if applicable */
  producingRunId?: UUID;
  /** Parent manifest if this is an update */
  parentManifestId?: UUID;
  /** QA/evaluation results */
  evaluationResults?: EvaluationResult[];
  /** Custom metadata */
  metadata: Record<string, unknown>;
}

export interface ManifestEntry {
  /** Path within the manifest tree */
  path: string;
  /** Referenced artifact or nested manifest */
  ref: ArtifactRef | ManifestRef;
  /** Entry-specific metadata */
  metadata?: Record<string, unknown>;
}

export interface ArtifactRef {
  type: 'artifact';
  artifactId: UUID;
  contentHash: ContentHash;
}

export interface ManifestRef {
  type: 'manifest';
  manifestId: UUID;
}

export interface CaptureMethod {
  tool: string;
  toolVersion: string;
  configHash: ContentHash;
  timestamp: Timestamp;
}

export interface EvaluationResult {
  evaluationId: UUID;
  name: string;
  passed: boolean;
  score?: number;
  details?: Record<string, unknown>;
  timestamp: Timestamp;
}

export type PointerType = 'bundle_head' | 'corpus_head' | 'kb_index_head' | 'model_head' | 'project_head';

/**
 * Pointer - Mutable HEAD reference
 * Used for bundle_head, corpus_head, kb_index_head, model_head
 */
export interface Pointer extends TenantScopedEntity {
  type: PointerType;
  name: string;
  /** Current manifest ID this pointer references */
  manifestId: UUID;
  /** Project scope if applicable */
  projectId?: UUID;
  /** Move history for audit */
  moveHistory: PointerMove[];
}

export interface PointerMove {
  fromManifestId: UUID | null;
  toManifestId: UUID;
  movedAt: Timestamp;
  movedBy: UUID;
  reason: 'publish' | 'promote' | 'revert' | 'migration';
  runId?: UUID;
}

// ============================================================================
// Bundles & Corpora
// ============================================================================

export interface Bundle extends TenantScopedEntity {
  name: string;
  description?: string;
  projectId?: UUID;
  /** HEAD pointer for this bundle */
  headPointerId: UUID;
  /** Semantic type of the bundle */
  semantics?: 'snapshot' | 'dataroom' | 'research_output' | 'analysis_output';
  /** Custom metadata */
  metadata: Record<string, unknown>;
}

export type GovernanceLevel = 'standard' | 'governed' | 'certified';

export interface Corpus extends TenantScopedEntity {
  name: string;
  description?: string;
  projectId?: UUID;
  /** HEAD pointer for this corpus */
  headPointerId: UUID;
  /** Governance profile */
  governanceProfile: GovernanceProfile;
  /** Downstream dependencies (KBs, other corpora) */
  downstreamDependencies: CorpusDependency[];
  /** Custom metadata */
  metadata: Record<string, unknown>;
}

export interface GovernanceProfile {
  level: GovernanceLevel;
  requiredGates: string[];
  approvalWorkflow?: ApprovalWorkflow;
  recertScheduleDays?: number;
  retentionDays?: number;
}

export interface ApprovalWorkflow {
  stages: ApprovalStage[];
  requireAllApprovers: boolean;
}

export interface ApprovalStage {
  name: string;
  approverIds: UUID[];
  minApprovals: number;
}

export interface CorpusDependency {
  dependentType: 'kb' | 'corpus' | 'model';
  dependentId: UUID;
  dependencyType: 'source' | 'derived';
}

// ============================================================================
// Runs & Workflow (Section 3.4)
// ============================================================================

export type RunStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'paused';

export type RunType = 'agentic' | 'deterministic' | 'hybrid';

/**
 * Run - Execution instance (agentic, deterministic, or hybrid)
 */
export interface Run extends ProjectScopedEntity {
  type: RunType;
  status: RunStatus;
  /** Session that initiated this run */
  sessionId?: UUID;
  /** Thread context if applicable */
  threadId?: UUID;
  /** Agent that executed this run */
  agentId?: UUID;
  /** Workflow definition if using a template */
  workflowDefinitionId?: UUID;
  /** Pinned input manifest IDs */
  inputManifestIds: UUID[];
  /** Output manifest ID once complete */
  outputManifestId?: UUID;
  /** Checkpoints for resume capability */
  checkpoints: RunCheckpoint[];
  /** Timing information */
  startedAt?: Timestamp;
  completedAt?: Timestamp;
  /** Error information if failed */
  error?: RunError;
  /** Resource usage */
  usage?: RunUsage;
  /** Custom metadata */
  metadata: Record<string, unknown>;
}

export interface RunCheckpoint {
  id: UUID;
  stepIndex: number;
  createdAt: Timestamp;
  state: Record<string, unknown>;
}

export interface RunError {
  code: string;
  message: string;
  stack?: string;
  stepId?: UUID;
}

export interface RunUsage {
  totalTokens: number;
  promptTokens: number;
  completionTokens: number;
  toolCalls: number;
  retrievalQueries: number;
  durationMs: number;
}

export interface WorkflowDefinition extends TenantScopedEntity {
  name: string;
  description?: string;
  version: SemanticVersion;
  /** Workflow steps */
  steps: WorkflowStep[];
  /** Required inputs */
  inputSchema?: SchemaRef;
  /** Expected outputs */
  outputSchema?: SchemaRef;
  /** Governance requirements */
  governanceLevel?: GovernanceLevel;
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: 'tool' | 'agent' | 'gate' | 'branch' | 'parallel';
  config: Record<string, unknown>;
  dependencies: string[];
}

// ============================================================================
// Agents & Sessions (Section 3.5)
// ============================================================================

export interface AgentDefinition extends TenantScopedEntity {
  name: string;
  description?: string;
  version: SemanticVersion;
  /** Allowed tools */
  allowedTools: string[];
  /** Allowed connectors */
  allowedConnectors: UUID[];
  /** Retrieval profiles this agent can use */
  retrievalProfiles: string[];
  /** Policy template requirements */
  policyTemplateId?: UUID;
  /** Prompt assets */
  promptAssets: PromptAsset[];
  /** Budget limits */
  budgetLimits?: AgentBudgetLimits;
}

export interface PromptAsset {
  name: string;
  content: string;
  type: 'system' | 'user' | 'assistant' | 'tool_description';
}

export interface AgentBudgetLimits {
  maxTokensPerRun: number;
  maxToolCallsPerRun: number;
  maxRetrievalQueriesPerRun: number;
  maxDurationMs: number;
}

export interface AgentTeam extends TenantScopedEntity {
  name: string;
  description?: string;
  agentIds: UUID[];
  /** Shared tool permissions */
  allowedTools: string[];
  /** Shared KB access */
  allowedKbIds: UUID[];
  /** Shared budget */
  sharedBudget?: AgentBudgetLimits;
}

export type SessionType = 'research_vm' | 'analysis' | 'modelling';
export type SessionStatus = 'active' | 'suspended' | 'closed';

export interface Session extends ProjectScopedEntity {
  type: SessionType;
  status: SessionStatus;
  userId: UUID;
  /** Compute realm binding */
  computeRealmId?: UUID;
  /** Mounted data assets */
  mounts: SessionMount[];
  /** Pinned context (artifacts, claims, etc.) */
  pinnedContext: PinnedContextItem[];
  /** Ephemeral filesystem state (for research VMs) */
  sessionFsState?: Record<string, unknown>;
  startedAt: Timestamp;
  closedAt?: Timestamp;
}

export interface SessionMount {
  dataAssetType: 'bundle' | 'corpus' | 'kb' | 'model' | 'skill_pack';
  dataAssetId: UUID;
  manifestId: UUID;
  mountPath: string;
  mode: 'readonly' | 'checkout';
}

export interface PinnedContextItem {
  type: 'artifact' | 'manifest' | 'claim' | 'evidence' | 'thread';
  id: UUID;
  label?: string;
  pinnedAt: Timestamp;
}

// ============================================================================
// Threads (Conversation Context)
// ============================================================================

export interface Thread extends ProjectScopedEntity {
  title?: string;
  sessionId?: UUID;
  messages: ThreadMessage[];
  pinnedContext: PinnedContextItem[];
  metadata: Record<string, unknown>;
}

export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export interface ThreadMessage {
  id: UUID;
  role: MessageRole;
  content: string;
  /** Attached artifacts */
  attachments: UUID[];
  /** Tool calls if assistant message */
  toolCalls?: ToolCall[];
  /** Tool result if tool message */
  toolResult?: ToolResult;
  createdAt: Timestamp;
  metadata: Record<string, unknown>;
}

export interface ToolCall {
  id: string;
  toolName: string;
  args: Record<string, unknown>;
}

export interface ToolResult {
  toolCallId: string;
  success: boolean;
  output: unknown;
  artifactIds?: UUID[];
}
