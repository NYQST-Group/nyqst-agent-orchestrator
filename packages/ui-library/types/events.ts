/**
 * Run Ledger Event types
 * Canonical logging for agentic interactions (Section 7 of reference design)
 */

import type { UUID, Timestamp, ContentHash } from './core';

// ============================================================================
// Base Event Types
// ============================================================================

export interface BaseEvent {
  id: UUID;
  timestamp: Timestamp;
  runId: UUID;
  stepId?: UUID;
  threadId?: UUID;
  sessionId?: UUID;
  /** Correlation ID for tracking related events */
  correlationId?: UUID;
  /** Causality chain */
  causedBy?: UUID;
  /** Principal who triggered the event */
  principalId: UUID;
  /** Visibility level */
  visibility: 'public' | 'internal' | 'redacted';
}

// ============================================================================
// Event Type Union
// ============================================================================

export type RunLedgerEvent =
  | ThreadMessageCreatedEvent
  | AgentPlanProposedEvent
  | AgentPlanUpdatedEvent
  | AgentActionProposedEvent
  | HumanCommentAddedEvent
  | HumanApprovalRecordedEvent
  | ToolCallStartedEvent
  | ToolCallCompletedEvent
  | RetrievalQueryEvent
  | RetrievalResultEvent
  | ArtifactEmittedEvent
  | ManifestCreatedEvent
  | PointerMovedEvent
  | DiffDetectedEvent
  | EvaluationStartedEvent
  | EvaluationCompletedEvent
  | DegradationHookTriggeredEvent
  | SessionStartedEvent
  | SessionClosedEvent
  | RunCheckpointCreatedEvent
  | RunCompletedEvent
  | RunFailedEvent;

export type EventCategory =
  | 'conversation'
  | 'planning'
  | 'tooling'
  | 'retrieval'
  | 'artifact'
  | 'governance'
  | 'evaluation'
  | 'lifecycle';

// ============================================================================
// Conversation and Planning Events
// ============================================================================

export interface ThreadMessageCreatedEvent extends BaseEvent {
  type: 'thread.message.created';
  category: 'conversation';
  payload: {
    messageId: UUID;
    role: 'user' | 'assistant' | 'system' | 'tool';
    content: string;
    attachmentIds: UUID[];
  };
}

export interface AgentPlanProposedEvent extends BaseEvent {
  type: 'agent.plan.proposed';
  category: 'planning';
  payload: {
    planArtifactId: UUID;
    planSummary: string;
    steps: PlanStep[];
    expectedOutputs: string[];
  };
}

export interface AgentPlanUpdatedEvent extends BaseEvent {
  type: 'agent.plan.updated';
  category: 'planning';
  payload: {
    planArtifactId: UUID;
    previousPlanArtifactId: UUID;
    changeDescription: string;
    updatedSteps: PlanStep[];
  };
}

export interface PlanStep {
  id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'failed';
  dependencies: string[];
  estimatedOutputs?: string[];
}

export interface AgentActionProposedEvent extends BaseEvent {
  type: 'agent.action.proposed';
  category: 'planning';
  payload: {
    actionType: 'publish' | 'promote' | 'run' | 'create_kb_index' | 'create_claims' | 'query_db';
    actionDescription: string;
    requiredApproval: boolean;
    targetIds?: UUID[];
  };
}

export interface HumanCommentAddedEvent extends BaseEvent {
  type: 'human.comment.added';
  category: 'conversation';
  payload: {
    comment: string;
    targetType?: 'plan' | 'step' | 'artifact' | 'claim';
    targetId?: UUID;
  };
}

export interface HumanApprovalRecordedEvent extends BaseEvent {
  type: 'human.approval.recorded';
  category: 'governance';
  payload: {
    decisionId: UUID;
    outcome: 'approved' | 'rejected' | 'deferred';
    rationale?: string;
    targetType: 'action' | 'plan' | 'promotion' | 'claim';
    targetId: UUID;
  };
}

// ============================================================================
// Tooling Events
// ============================================================================

export interface ToolCallStartedEvent extends BaseEvent {
  type: 'tool.call.started';
  category: 'tooling';
  payload: {
    toolCallId: string;
    toolName: string;
    toolVersion: string;
    argsHash: ContentHash;
    args: Record<string, unknown>;
  };
}

export interface ToolCallCompletedEvent extends BaseEvent {
  type: 'tool.call.completed';
  category: 'tooling';
  payload: {
    toolCallId: string;
    toolName: string;
    success: boolean;
    durationMs: number;
    outputArtifactIds: UUID[];
    error?: {
      code: string;
      message: string;
    };
  };
}

// ============================================================================
// Retrieval Events
// ============================================================================

export interface RetrievalQueryEvent extends BaseEvent {
  type: 'retrieval.query';
  category: 'retrieval';
  payload: {
    queryId: UUID;
    knowledgeBaseId: UUID;
    profileId: string;
    query: string;
    filters?: Record<string, unknown>;
    topK: number;
  };
}

export interface RetrievalResultEvent extends BaseEvent {
  type: 'retrieval.result';
  category: 'retrieval';
  payload: {
    queryId: UUID;
    resultCount: number;
    topKArtifactIds: UUID[];
    scores: number[];
    durationMs: number;
  };
}

// ============================================================================
// Artifact and Manifest Events
// ============================================================================

export interface ArtifactEmittedEvent extends BaseEvent {
  type: 'artifact.emitted';
  category: 'artifact';
  payload: {
    artifactId: UUID;
    contentHash: ContentHash;
    logicalType: string;
    mimeType: string;
    sizeBytes: number;
    filename?: string;
  };
}

export interface ManifestCreatedEvent extends BaseEvent {
  type: 'manifest.created';
  category: 'artifact';
  payload: {
    manifestId: UUID;
    kind: string;
    entryCount: number;
    parentManifestId?: UUID;
  };
}

export interface PointerMovedEvent extends BaseEvent {
  type: 'pointer.moved';
  category: 'governance';
  payload: {
    pointerId: UUID;
    pointerName: string;
    reason: 'publish' | 'promote' | 'revert' | 'migration';
    fromManifestId: UUID | null;
    toManifestId: UUID;
    bundleId?: UUID;
    corpusId?: UUID;
  };
}

// ============================================================================
// Diff and Evaluation Events
// ============================================================================

export interface DiffDetectedEvent extends BaseEvent {
  type: 'diff.detected';
  category: 'evaluation';
  payload: {
    diffId: UUID;
    sourceType: 'artifact' | 'manifest' | 'corpus';
    sourceId: UUID;
    previousVersionId: UUID;
    currentVersionId: UUID;
    changeStats: {
      added: number;
      removed: number;
      modified: number;
    };
    significantChanges: string[];
  };
}

export interface EvaluationStartedEvent extends BaseEvent {
  type: 'evaluation.started';
  category: 'evaluation';
  payload: {
    evaluationId: UUID;
    evaluationSuiteId: UUID;
    targetType: 'corpus' | 'model' | 'kb_index' | 'claim_set';
    targetId: UUID;
    gateNames: string[];
  };
}

export interface EvaluationCompletedEvent extends BaseEvent {
  type: 'evaluation.completed';
  category: 'evaluation';
  payload: {
    evaluationId: UUID;
    passed: boolean;
    results: {
      gateName: string;
      passed: boolean;
      score?: number;
      message?: string;
    }[];
    durationMs: number;
  };
}

export interface DegradationHookTriggeredEvent extends BaseEvent {
  type: 'degradation.hook.triggered';
  category: 'evaluation';
  payload: {
    hookType: 're_index' | 're_evaluate' | 'notify' | 'block';
    reason: string;
    triggeredBy: 'diff' | 'evaluation_failure' | 'dependency_change';
    affectedIds: UUID[];
    actions: string[];
  };
}

// ============================================================================
// Session Lifecycle Events
// ============================================================================

export interface SessionStartedEvent extends BaseEvent {
  type: 'session.started';
  category: 'lifecycle';
  payload: {
    sessionType: 'research_vm' | 'analysis' | 'modelling';
    projectId: UUID;
    userId: UUID;
    mounts: {
      dataAssetId: UUID;
      manifestId: UUID;
      mountPath: string;
    }[];
  };
}

export interface SessionClosedEvent extends BaseEvent {
  type: 'session.closed';
  category: 'lifecycle';
  payload: {
    durationMs: number;
    artifactsPublished: number;
    runsCompleted: number;
  };
}

export interface RunCheckpointCreatedEvent extends BaseEvent {
  type: 'run.checkpoint.created';
  category: 'lifecycle';
  payload: {
    checkpointId: UUID;
    stepIndex: number;
    stateSize: number;
  };
}

export interface RunCompletedEvent extends BaseEvent {
  type: 'run.completed';
  category: 'lifecycle';
  payload: {
    outputManifestId: UUID;
    artifactCount: number;
    durationMs: number;
    usage: {
      totalTokens: number;
      toolCalls: number;
      retrievalQueries: number;
    };
  };
}

export interface RunFailedEvent extends BaseEvent {
  type: 'run.failed';
  category: 'lifecycle';
  payload: {
    errorCode: string;
    errorMessage: string;
    failedAtStep?: string;
    recoverable: boolean;
    lastCheckpointId?: UUID;
  };
}

// ============================================================================
// Event Filtering and Querying
// ============================================================================

export interface EventFilter {
  runIds?: UUID[];
  sessionIds?: UUID[];
  threadIds?: UUID[];
  types?: RunLedgerEvent['type'][];
  categories?: EventCategory[];
  principalIds?: UUID[];
  fromTimestamp?: Timestamp;
  toTimestamp?: Timestamp;
  visibility?: ('public' | 'internal')[];
}

export interface EventQueryResult {
  events: RunLedgerEvent[];
  totalCount: number;
  hasMore: boolean;
  cursor?: string;
}
