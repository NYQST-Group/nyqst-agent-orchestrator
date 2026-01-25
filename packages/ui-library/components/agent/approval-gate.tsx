/**
 * Approval Gate Component
 *
 * Based on research findings about human-in-the-loop patterns:
 * - LangGraph `interrupt()` for pausing mid-execution
 * - HumanLayer SDK's `@require_approval` decorators
 * - Clear consent layers with safe defaults
 * - One-click rollback capability
 */

import * as React from 'react';
import { createContext, useContext, useState, useCallback } from 'react';
import { cn } from '../../lib/utils';

export type ApprovalStatus =
  | 'pending'      // Waiting for user decision
  | 'approved'     // User approved
  | 'rejected'     // User rejected
  | 'modified'     // User approved with modifications
  | 'expired';     // Approval request timed out

export interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  risk: 'low' | 'medium' | 'high' | 'critical';
  details?: Record<string, unknown>;
  proposedChanges?: Array<{
    type: 'create' | 'update' | 'delete';
    target: string;
    before?: unknown;
    after?: unknown;
  }>;
  status: ApprovalStatus;
  requestedAt: Date;
  respondedAt?: Date;
  expiresAt?: Date;
  response?: {
    decision: 'approve' | 'reject' | 'modify';
    reason?: string;
    modifications?: Record<string, unknown>;
  };
}

interface ApprovalFlowContextValue {
  pendingRequests: ApprovalRequest[];
  requestApproval: (request: Omit<ApprovalRequest, 'id' | 'status' | 'requestedAt'>) => Promise<ApprovalRequest>;
  respond: (id: string, decision: 'approve' | 'reject' | 'modify', options?: { reason?: string; modifications?: Record<string, unknown> }) => void;
}

const ApprovalFlowContext = createContext<ApprovalFlowContextValue | null>(null);

export function useApprovalFlow() {
  const context = useContext(ApprovalFlowContext);
  if (!context) {
    throw new Error('useApprovalFlow must be used within ApprovalGateProvider');
  }
  return context;
}

interface ApprovalGateProviderProps {
  children: React.ReactNode;
  onApprovalRequest?: (request: ApprovalRequest) => void;
  onApprovalResponse?: (request: ApprovalRequest) => void;
}

export function ApprovalGateProvider({
  children,
  onApprovalRequest,
  onApprovalResponse,
}: ApprovalGateProviderProps) {
  const [requests, setRequests] = useState<Map<string, { request: ApprovalRequest; resolve: (req: ApprovalRequest) => void }>>(new Map());

  const requestApproval = useCallback(async (
    requestData: Omit<ApprovalRequest, 'id' | 'status' | 'requestedAt'>
  ): Promise<ApprovalRequest> => {
    const id = `approval-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const request: ApprovalRequest = {
      ...requestData,
      id,
      status: 'pending',
      requestedAt: new Date(),
    };

    return new Promise((resolve) => {
      setRequests(prev => new Map(prev).set(id, { request, resolve }));
      onApprovalRequest?.(request);
    });
  }, [onApprovalRequest]);

  const respond = useCallback((
    id: string,
    decision: 'approve' | 'reject' | 'modify',
    options?: { reason?: string; modifications?: Record<string, unknown> }
  ) => {
    setRequests(prev => {
      const next = new Map(prev);
      const entry = next.get(id);
      if (entry) {
        const updatedRequest: ApprovalRequest = {
          ...entry.request,
          status: decision === 'approve' ? 'approved' : decision === 'reject' ? 'rejected' : 'modified',
          respondedAt: new Date(),
          response: {
            decision,
            reason: options?.reason,
            modifications: options?.modifications,
          },
        };
        entry.resolve(updatedRequest);
        next.delete(id);
        onApprovalResponse?.(updatedRequest);
      }
      return next;
    });
  }, [onApprovalResponse]);

  const pendingRequests = Array.from(requests.values()).map(e => e.request);

  return (
    <ApprovalFlowContext.Provider value={{ pendingRequests, requestApproval, respond }}>
      {children}
    </ApprovalFlowContext.Provider>
  );
}

const RISK_STYLES: Record<ApprovalRequest['risk'], { bg: string; border: string; label: string }> = {
  low: {
    bg: 'bg-green-50 dark:bg-green-900/10',
    border: 'border-green-200 dark:border-green-800',
    label: 'Low Risk',
  },
  medium: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/10',
    border: 'border-yellow-200 dark:border-yellow-800',
    label: 'Medium Risk',
  },
  high: {
    bg: 'bg-orange-50 dark:bg-orange-900/10',
    border: 'border-orange-200 dark:border-orange-800',
    label: 'High Risk',
  },
  critical: {
    bg: 'bg-red-50 dark:bg-red-900/10',
    border: 'border-red-200 dark:border-red-800',
    label: 'Critical Risk',
  },
};

interface ApprovalGateProps {
  request: ApprovalRequest;
  className?: string;
  showChanges?: boolean;
  onApprove?: () => void;
  onReject?: (reason?: string) => void;
  onModify?: (modifications: Record<string, unknown>) => void;
}

export function ApprovalGate({
  request,
  className,
  showChanges = true,
  onApprove,
  onReject,
  onModify,
}: ApprovalGateProps) {
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectInput, setShowRejectInput] = useState(false);
  const riskStyle = RISK_STYLES[request.risk];

  const handleReject = () => {
    if (showRejectInput) {
      onReject?.(rejectReason || undefined);
      setShowRejectInput(false);
      setRejectReason('');
    } else {
      setShowRejectInput(true);
    }
  };

  return (
    <div className={cn('rounded-lg border p-4', riskStyle.bg, riskStyle.border, className)}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-medium">{request.action}</span>
            <span className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              request.risk === 'critical' && 'bg-red-500 text-white',
              request.risk === 'high' && 'bg-orange-500 text-white',
              request.risk === 'medium' && 'bg-yellow-500 text-black',
              request.risk === 'low' && 'bg-green-500 text-white',
            )}>
              {riskStyle.label}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">{request.description}</p>
        </div>
      </div>

      {/* Proposed Changes */}
      {showChanges && request.proposedChanges && request.proposedChanges.length > 0 && (
        <div className="mb-4 space-y-2">
          <span className="text-xs font-medium text-muted-foreground">Proposed Changes:</span>
          {request.proposedChanges.map((change, index) => (
            <div key={index} className="p-2 rounded bg-background/50 text-xs">
              <div className="flex items-center gap-2 mb-1">
                <span className={cn(
                  'px-1.5 py-0.5 rounded font-medium',
                  change.type === 'create' && 'bg-green-100 text-green-700',
                  change.type === 'update' && 'bg-blue-100 text-blue-700',
                  change.type === 'delete' && 'bg-red-100 text-red-700',
                )}>
                  {change.type.toUpperCase()}
                </span>
                <span className="font-mono">{change.target}</span>
              </div>
              {change.type === 'update' && change.before !== undefined && (
                <div className="mt-1 grid grid-cols-2 gap-2">
                  <div className="p-1 rounded bg-red-50 dark:bg-red-900/10">
                    <span className="text-red-600 dark:text-red-400">- </span>
                    <code>{JSON.stringify(change.before)}</code>
                  </div>
                  <div className="p-1 rounded bg-green-50 dark:bg-green-900/10">
                    <span className="text-green-600 dark:text-green-400">+ </span>
                    <code>{JSON.stringify(change.after)}</code>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Reject reason input */}
      {showRejectInput && (
        <div className="mb-4">
          <input
            type="text"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Reason for rejection (optional)"
            className="w-full px-3 py-2 text-sm border rounded-md bg-background"
            autoFocus
          />
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onApprove}
          className={cn(
            'flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors',
            'bg-green-600 hover:bg-green-700 text-white',
            'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
          )}
        >
          Approve
        </button>
        <button
          onClick={handleReject}
          className={cn(
            'flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors',
            'bg-red-600 hover:bg-red-700 text-white',
            'focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2'
          )}
        >
          {showRejectInput ? 'Confirm Reject' : 'Reject'}
        </button>
        {onModify && (
          <button
            onClick={() => onModify({})}
            className={cn(
              'px-4 py-2 rounded-md text-sm font-medium transition-colors',
              'bg-muted hover:bg-muted/80',
              'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2'
            )}
          >
            Modify
          </button>
        )}
      </div>

      {/* Timestamp */}
      <p className="mt-3 text-xs text-muted-foreground text-center">
        Requested {request.requestedAt.toLocaleTimeString()}
        {request.expiresAt && (
          <> (expires {request.expiresAt.toLocaleTimeString()})</>
        )}
      </p>
    </div>
  );
}
