/**
 * Tool Visibility Components
 *
 * Based on research findings about transparency patterns:
 * - Visible thought log with human-readable explanations
 * - Tool invocation disclosure showing what's called and why
 * - Confidence metrics displaying agent certainty
 * - Source attribution linking outputs to retrieved context
 */

import * as React from 'react';
import { useState } from 'react';
import { cn } from '../../lib/utils';

export type ToolCallStatus =
  | 'pending'
  | 'executing'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface ToolCall {
  id: string;
  name: string;
  description?: string;
  parameters?: Record<string, unknown>;
  result?: unknown;
  error?: string;
  status: ToolCallStatus;
  startedAt?: Date;
  completedAt?: Date;
  confidence?: number; // 0-1
  sources?: Array<{
    id: string;
    title: string;
    excerpt?: string;
  }>;
}

interface ToolVisibilityProps {
  toolCalls: ToolCall[];
  className?: string;
  showParameters?: boolean;
  showResults?: boolean;
  showSources?: boolean;
  expandedByDefault?: boolean;
}

const STATUS_STYLES: Record<ToolCallStatus, { bg: string; icon: string; label: string }> = {
  pending: {
    bg: 'bg-muted',
    icon: '...',
    label: 'Queued',
  },
  executing: {
    bg: 'bg-blue-100 dark:bg-blue-900/20',
    icon: '...',
    label: 'Running',
  },
  completed: {
    bg: 'bg-green-100 dark:bg-green-900/20',
    icon: '...',
    label: 'Done',
  },
  failed: {
    bg: 'bg-red-100 dark:bg-red-900/20',
    icon: '...',
    label: 'Failed',
  },
  cancelled: {
    bg: 'bg-yellow-100 dark:bg-yellow-900/20',
    icon: '...',
    label: 'Cancelled',
  },
};

export function ToolVisibility({
  toolCalls,
  className,
  showParameters = false,
  showResults = true,
  showSources = true,
  expandedByDefault = false,
}: ToolVisibilityProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(
    expandedByDefault ? new Set(toolCalls.map(t => t.id)) : new Set()
  );

  const toggleExpanded = (id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  if (toolCalls.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <span>Agent Actions</span>
        <span className="px-1.5 py-0.5 rounded bg-muted">{toolCalls.length}</span>
      </div>

      <div className="space-y-1">
        {toolCalls.map((tool) => {
          const status = STATUS_STYLES[tool.status];
          const isExpanded = expandedIds.has(tool.id);
          const duration = tool.startedAt && tool.completedAt
            ? tool.completedAt.getTime() - tool.startedAt.getTime()
            : null;

          return (
            <div
              key={tool.id}
              className={cn(
                'rounded-lg border transition-colors',
                status.bg
              )}
            >
              {/* Header */}
              <button
                onClick={() => toggleExpanded(tool.id)}
                className="w-full flex items-center justify-between p-2 text-left"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs">{status.icon}</span>
                  <span className="font-mono text-sm">{tool.name}</span>
                  {tool.confidence !== undefined && (
                    <span className="text-xs text-muted-foreground">
                      {Math.round(tool.confidence * 100)}% confident
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {duration !== null && (
                    <span>{duration}ms</span>
                  )}
                  <span>{isExpanded ? '-' : '+'}</span>
                </div>
              </button>

              {/* Expanded content */}
              {isExpanded && (
                <div className="px-2 pb-2 space-y-2 text-sm">
                  {tool.description && (
                    <p className="text-muted-foreground">{tool.description}</p>
                  )}

                  {showParameters && tool.parameters && Object.keys(tool.parameters).length > 0 && (
                    <div className="space-y-1">
                      <span className="text-xs font-medium">Parameters:</span>
                      <pre className="p-2 rounded bg-muted/50 text-xs overflow-auto">
                        {JSON.stringify(tool.parameters, null, 2)}
                      </pre>
                    </div>
                  )}

                  {showResults && tool.status === 'completed' && tool.result !== undefined && (
                    <div className="space-y-1">
                      <span className="text-xs font-medium">Result:</span>
                      <pre className="p-2 rounded bg-muted/50 text-xs overflow-auto max-h-40">
                        {typeof tool.result === 'string'
                          ? tool.result
                          : JSON.stringify(tool.result, null, 2)}
                      </pre>
                    </div>
                  )}

                  {tool.status === 'failed' && tool.error && (
                    <div className="p-2 rounded bg-destructive/10 text-destructive text-xs">
                      {tool.error}
                    </div>
                  )}

                  {showSources && tool.sources && tool.sources.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-xs font-medium">Sources:</span>
                      <div className="space-y-1">
                        {tool.sources.map((source) => (
                          <div
                            key={source.id}
                            className="p-2 rounded bg-muted/50 text-xs"
                          >
                            <span className="font-medium">{source.title}</span>
                            {source.excerpt && (
                              <p className="mt-1 text-muted-foreground line-clamp-2">
                                {source.excerpt}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
