/**
 * Evidence, Claims, and Decisions types
 * Modelling layer primitives (Section 3.5 of reference design)
 */

import type { UUID, Timestamp, TenantScopedEntity, ProjectScopedEntity } from './core';

// ============================================================================
// Evidence Spans
// ============================================================================

export interface EvidenceSpan extends ProjectScopedEntity {
  /** Source document artifact */
  documentArtifactId: UUID;
  /** DocIR block reference */
  blockId?: string;
  /** Page number (1-indexed) */
  pageNumber?: number;
  /** Character offset start */
  startOffset: number;
  /** Character offset end */
  endOffset: number;
  /** Extracted text content */
  content: string;
  /** Confidence score if AI-extracted */
  confidence?: number;
  /** Extraction method */
  extractionMethod: 'manual' | 'ai_extracted' | 'rule_based';
  /** Run that created this evidence */
  createdByRunId?: UUID;
  metadata: Record<string, unknown>;
}

// ============================================================================
// Claims
// ============================================================================

export type ClaimType =
  | 'requirement'
  | 'control'
  | 'mapping'
  | 'risk'
  | 'interpretation'
  | 'fact'
  | 'assertion'
  | 'finding';

export type ClaimStatus =
  | 'draft'
  | 'proposed'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'superseded';

export type ClaimConfidence = 'low' | 'medium' | 'high' | 'verified';

export interface Claim extends ProjectScopedEntity {
  type: ClaimType;
  status: ClaimStatus;
  /** Short title/summary */
  title: string;
  /** Full claim content */
  content: string;
  /** Confidence level */
  confidence: ClaimConfidence;
  /** Tags for categorization */
  tags: string[];
  /** Schema/type if structured */
  claimSchemaId?: UUID;
  /** Structured data if applicable */
  structuredData?: Record<string, unknown>;
  /** Parent claim if this is a sub-claim */
  parentClaimId?: UUID;
  /** Run that created this claim */
  createdByRunId?: UUID;
  /** Current owner/assignee */
  ownerId?: UUID;
  /** Review deadline */
  reviewDeadline?: Timestamp;
  metadata: Record<string, unknown>;
}

// ============================================================================
// Claim-Evidence Links
// ============================================================================

export type SupportType =
  | 'supports'
  | 'contradicts'
  | 'neutral'
  | 'partial_support'
  | 'requires_context';

export type LinkConfidence = 'low' | 'medium' | 'high';

export interface ClaimSupportLink extends ProjectScopedEntity {
  claimId: UUID;
  evidenceSpanId: UUID;
  supportType: SupportType;
  confidence: LinkConfidence;
  /** Explanation of the link */
  rationale?: string;
  /** Who created this link */
  createdBy: UUID;
  /** Run that created this link */
  createdByRunId?: UUID;
  metadata: Record<string, unknown>;
}

// ============================================================================
// Decisions
// ============================================================================

export type DecisionType =
  | 'approval'
  | 'rejection'
  | 'override'
  | 'sign_off'
  | 'escalation'
  | 'deferral';

export type DecisionContext =
  | 'claim_review'
  | 'corpus_promotion'
  | 'model_promotion'
  | 'gate_evaluation'
  | 'access_request';

export interface Decision extends ProjectScopedEntity {
  type: DecisionType;
  context: DecisionContext;
  /** What this decision applies to */
  subjectType: 'claim' | 'corpus' | 'model' | 'run' | 'artifact';
  subjectId: UUID;
  /** Decision maker */
  deciderId: UUID;
  /** Decision outcome */
  outcome: 'approved' | 'rejected' | 'deferred' | 'escalated';
  /** Rationale for the decision */
  rationale: string;
  /** Conditions attached to approval */
  conditions?: DecisionCondition[];
  /** Expiration if applicable */
  expiresAt?: Timestamp;
  /** Supersedes another decision */
  supersedesDecisionId?: UUID;
  /** Related run */
  runId?: UUID;
  metadata: Record<string, unknown>;
}

export interface DecisionCondition {
  type: 'time_limited' | 'scope_limited' | 'requires_followup' | 'pending_review';
  description: string;
  deadline?: Timestamp;
}

// ============================================================================
// Claim Sets (for bulk operations)
// ============================================================================

export interface ClaimSet extends ProjectScopedEntity {
  name: string;
  description?: string;
  /** Claims in this set */
  claimIds: UUID[];
  /** Bundle/corpus this claim set was derived from */
  sourceManifestId?: UUID;
  /** Run that created this claim set */
  createdByRunId?: UUID;
  /** Aggregate statistics */
  stats: ClaimSetStats;
  metadata: Record<string, unknown>;
}

export interface ClaimSetStats {
  totalClaims: number;
  byType: Record<ClaimType, number>;
  byStatus: Record<ClaimStatus, number>;
  byConfidence: Record<ClaimConfidence, number>;
  totalEvidenceLinks: number;
  avgEvidencePerClaim: number;
}

// ============================================================================
// Evidence Graphs (for provenance visualization)
// ============================================================================

export interface EvidenceGraph {
  nodes: EvidenceGraphNode[];
  edges: EvidenceGraphEdge[];
}

export type EvidenceGraphNodeType = 'claim' | 'evidence' | 'document' | 'decision';

export interface EvidenceGraphNode {
  id: UUID;
  type: EvidenceGraphNodeType;
  label: string;
  data: Record<string, unknown>;
}

export interface EvidenceGraphEdge {
  id: string;
  source: UUID;
  target: UUID;
  type: 'supports' | 'contradicts' | 'derived_from' | 'approved_by' | 'contains';
  label?: string;
  weight?: number;
}
