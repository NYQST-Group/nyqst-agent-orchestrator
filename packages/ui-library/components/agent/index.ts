/**
 * Agent-First UI Components
 * Based on research into Claude Artifacts, Cursor, v0, Bolt.new, Devin patterns
 */

export { AutonomySlider, useAutonomyContext, AutonomyProvider } from './autonomy-slider';
export type { AutonomyLevel } from './autonomy-slider';

export { ToolVisibility } from './tool-visibility';
export type { ToolCall, ToolCallStatus } from './tool-visibility';

export { ReasoningPanel, ThinkingIndicator } from './reasoning-panel';
export type { ReasoningStep } from './reasoning-panel';

export { ApprovalGate, ApprovalGateProvider, useApprovalFlow } from './approval-gate';
export type { ApprovalRequest, ApprovalStatus } from './approval-gate';

export { TrustIndicator, getTrustLevelFromScore } from './trust-indicator';
export type { TrustLevel } from './trust-indicator';
