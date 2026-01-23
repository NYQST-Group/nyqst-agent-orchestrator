/**
 * Connector System types
 * Business system integration (Section 11 & 15 of reference design)
 */

import type { UUID, Timestamp, TenantScopedEntity, ContentHash } from './core';

// ============================================================================
// Connector Definition
// ============================================================================

export type ConnectorProvider =
  | 'slack'
  | 'hubspot'
  | 'monday'
  | 'jira'
  | 'confluence'
  | 'sharepoint'
  | 'google_drive'
  | 'notion'
  | 'asana'
  | 'salesforce'
  | 'custom';

export type ConnectorStatus = 'active' | 'disconnected' | 'error' | 'rate_limited';

export interface Connector extends TenantScopedEntity {
  provider: ConnectorProvider;
  name: string;
  description?: string;
  status: ConnectorStatus;
  /** Auth configuration reference */
  authConfigId: UUID;
  /** Granted scopes */
  scopes: string[];
  /** Rate limit configuration */
  rateLimitPolicy: RateLimitPolicy;
  /** Webhook subscriptions */
  webhookSubscriptions: WebhookSubscription[];
  /** Last successful sync */
  lastSyncAt?: Timestamp;
  /** Error information if status is error */
  lastError?: ConnectorError;
  /** Custom configuration */
  config: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface RateLimitPolicy {
  requestsPerMinute: number;
  requestsPerHour: number;
  burstLimit: number;
  retryAfterMs: number;
}

export interface WebhookSubscription {
  id: string;
  eventTypes: string[];
  endpoint: string;
  secret?: string;
  active: boolean;
  createdAt: Timestamp;
}

export interface ConnectorError {
  code: string;
  message: string;
  occurredAt: Timestamp;
  retryable: boolean;
}

// ============================================================================
// Auth Configuration
// ============================================================================

export type AuthType = 'oauth2' | 'api_key' | 'basic' | 'custom';

export interface ConnectorAuthConfig extends TenantScopedEntity {
  connectorId: UUID;
  authType: AuthType;
  /** Secret reference (stored in secrets manager) */
  secretRef: string;
  /** OAuth2 specific fields */
  oauth2Config?: OAuth2Config;
  /** Token expiry */
  expiresAt?: Timestamp;
  /** Refresh token available */
  refreshable: boolean;
}

export interface OAuth2Config {
  clientId: string;
  authorizationUrl: string;
  tokenUrl: string;
  scopes: string[];
  redirectUri: string;
}

// ============================================================================
// Connector Runs (Sync Jobs)
// ============================================================================

export type ConnectorRunType = 'full_sync' | 'incremental_sync' | 'webhook_process' | 'backfill';
export type ConnectorRunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface ConnectorRun extends TenantScopedEntity {
  connectorId: UUID;
  type: ConnectorRunType;
  status: ConnectorRunStatus;
  /** Sync cursor for incremental syncs */
  cursor?: string;
  /** Items processed */
  stats: ConnectorRunStats;
  /** Output artifacts/manifests */
  outputArtifactIds: UUID[];
  /** Timing */
  startedAt: Timestamp;
  completedAt?: Timestamp;
  /** Error if failed */
  error?: ConnectorError;
  metadata: Record<string, unknown>;
}

export interface ConnectorRunStats {
  itemsFetched: number;
  itemsCreated: number;
  itemsUpdated: number;
  itemsSkipped: number;
  itemsFailed: number;
  apiCallsMade: number;
}

// ============================================================================
// Canonical Work Coordination Entities (CDM-like)
// ============================================================================

/**
 * Canonical Account (Client)
 * Maps from HubSpot Company, Salesforce Account, etc.
 */
export interface CanonicalAccount extends TenantScopedEntity {
  name: string;
  domain?: string;
  industry?: string;
  size?: 'small' | 'medium' | 'large' | 'enterprise';
  status: 'prospect' | 'active' | 'churned' | 'archived';
  /** External system mappings */
  externalRefs: ExternalRef[];
  metadata: Record<string, unknown>;
}

/**
 * Canonical Contact
 * Maps from HubSpot Contact, Salesforce Contact, etc.
 */
export interface CanonicalContact extends TenantScopedEntity {
  accountId?: UUID;
  firstName: string;
  lastName: string;
  email?: string;
  phone?: string;
  title?: string;
  role?: string;
  /** External system mappings */
  externalRefs: ExternalRef[];
  metadata: Record<string, unknown>;
}

/**
 * Canonical Thread/Message
 * Maps from Slack messages, email threads, etc.
 */
export interface CanonicalThread extends TenantScopedEntity {
  projectId?: UUID;
  title?: string;
  channel?: string;
  participantIds: UUID[];
  messageCount: number;
  lastMessageAt: Timestamp;
  /** External system mappings */
  externalRefs: ExternalRef[];
  metadata: Record<string, unknown>;
}

export interface CanonicalMessage extends TenantScopedEntity {
  threadId: UUID;
  senderId: UUID;
  content: string;
  attachmentIds: UUID[];
  sentAt: Timestamp;
  /** External system mappings */
  externalRefs: ExternalRef[];
  metadata: Record<string, unknown>;
}

export interface ExternalRef {
  provider: ConnectorProvider;
  externalId: string;
  externalUrl?: string;
  syncedAt: Timestamp;
}

// ============================================================================
// Mapping Specs (Provider → Canonical)
// ============================================================================

export interface MappingSpec extends TenantScopedEntity {
  connectorId: UUID;
  provider: ConnectorProvider;
  version: string;
  /** Provider object model (raw) */
  providerSchema: Record<string, unknown>;
  /** Field mappings */
  fieldMappings: FieldMapping[];
  /** Identity resolution rules */
  identityRules: IdentityRule[];
  /** Permission mapping rules */
  permissionRules: PermissionRule[];
  /** Validation/evaluation suite */
  evaluationSuiteId?: UUID;
  /** Promoted status */
  promoted: boolean;
  promotedAt?: Timestamp;
  promotedBy?: UUID;
  metadata: Record<string, unknown>;
}

export interface FieldMapping {
  sourceField: string;
  targetField: string;
  targetEntity: 'account' | 'contact' | 'project' | 'task' | 'thread' | 'message' | 'document';
  transform?: FieldTransform;
  required: boolean;
  defaultValue?: unknown;
}

export type FieldTransformType =
  | 'direct'
  | 'lowercase'
  | 'uppercase'
  | 'trim'
  | 'date_parse'
  | 'json_extract'
  | 'regex_extract'
  | 'lookup'
  | 'custom';

export interface FieldTransform {
  type: FieldTransformType;
  config?: Record<string, unknown>;
}

export interface IdentityRule {
  entityType: string;
  matchFields: string[];
  strategy: 'exact' | 'fuzzy' | 'email_domain';
  createIfMissing: boolean;
}

export interface PermissionRule {
  externalPermission: string;
  internalRole: string;
  scopeType: 'tenant' | 'project' | 'resource';
}

// ============================================================================
// Webhook Events
// ============================================================================

export interface WebhookEvent extends TenantScopedEntity {
  connectorId: UUID;
  /** Raw event type from provider */
  rawEventType: string;
  /** Normalized event type */
  normalizedType: string;
  /** Raw payload */
  rawPayload: Record<string, unknown>;
  /** Normalized payload */
  normalizedPayload?: Record<string, unknown>;
  /** Processing status */
  processed: boolean;
  processedAt?: Timestamp;
  /** Triggered run if applicable */
  triggeredRunId?: UUID;
  /** Idempotency key */
  idempotencyKey: string;
  receivedAt: Timestamp;
}
