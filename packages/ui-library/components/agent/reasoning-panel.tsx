/**
 * Reasoning Panel Components
 *
 * Based on research findings:
 * - Devin's plan visualization with real-time updates
 * - AgentPrism's tree/timeline/sequence views
 * - LangSmith's step-through debugging
 * - Alan AI's reasoning graphs
 */

import * as React from 'react';
import { cn } from '../../lib/utils';

export interface ReasoningStep {
  id: string;
  type: 'thinking' | 'planning' | 'executing' | 'evaluating' | 'complete';
  title: string;
  content?: string;
  children?: ReasoningStep[];
  status: 'pending' | 'active' | 'complete' | 'failed';
  timestamp?: Date;
  duration?: number; // ms
}

interface ReasoningPanelProps {
  steps: ReasoningStep[];
  className?: string;
  view?: 'tree' | 'timeline' | 'compact';
  showTimestamps?: boolean;
  maxDepth?: number;
}

const STEP_TYPE_STYLES: Record<ReasoningStep['type'], { color: string; label: string }> = {
  thinking: { color: 'text-blue-500', label: 'Thinking' },
  planning: { color: 'text-purple-500', label: 'Planning' },
  executing: { color: 'text-green-500', label: 'Executing' },
  evaluating: { color: 'text-yellow-500', label: 'Evaluating' },
  complete: { color: 'text-muted-foreground', label: 'Complete' },
};

const STATUS_INDICATORS: Record<ReasoningStep['status'], string> = {
  pending: 'bg-muted-foreground/30',
  active: 'bg-blue-500 animate-pulse',
  complete: 'bg-green-500',
  failed: 'bg-red-500',
};

function TreeNode({
  step,
  depth = 0,
  maxDepth = 10,
  showTimestamps,
}: {
  step: ReasoningStep;
  depth?: number;
  maxDepth: number;
  showTimestamps: boolean;
}) {
  if (depth > maxDepth) return null;

  const typeStyle = STEP_TYPE_STYLES[step.type];
  const statusIndicator = STATUS_INDICATORS[step.status];

  return (
    <div className="relative">
      {/* Connection line */}
      {depth > 0 && (
        <div
          className="absolute left-0 top-0 w-px h-full bg-border -translate-x-3"
          style={{ marginTop: '-0.5rem' }}
        />
      )}

      <div className={cn('relative', depth > 0 && 'ml-6')}>
        {/* Horizontal connector */}
        {depth > 0 && (
          <div className="absolute left-0 top-3 w-3 h-px bg-border -translate-x-3" />
        )}

        {/* Step content */}
        <div className="flex items-start gap-2 py-1">
          <div className={cn('w-2 h-2 rounded-full mt-1.5 flex-shrink-0', statusIndicator)} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className={cn('text-xs font-medium', typeStyle.color)}>
                {typeStyle.label}
              </span>
              <span className="text-sm font-medium truncate">{step.title}</span>
              {showTimestamps && step.duration !== undefined && (
                <span className="text-xs text-muted-foreground ml-auto">
                  {step.duration}ms
                </span>
              )}
            </div>
            {step.content && (
              <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                {step.content}
              </p>
            )}
          </div>
        </div>

        {/* Children */}
        {step.children && step.children.length > 0 && (
          <div className="ml-1">
            {step.children.map((child) => (
              <TreeNode
                key={child.id}
                step={child}
                depth={depth + 1}
                maxDepth={maxDepth}
                showTimestamps={showTimestamps}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineView({
  steps,
  showTimestamps,
}: {
  steps: ReasoningStep[];
  showTimestamps: boolean;
}) {
  return (
    <div className="relative pl-4">
      {/* Vertical line */}
      <div className="absolute left-1.5 top-0 bottom-0 w-px bg-border" />

      {steps.map((step, index) => {
        const typeStyle = STEP_TYPE_STYLES[step.type];
        const statusIndicator = STATUS_INDICATORS[step.status];

        return (
          <div key={step.id} className="relative pb-4 last:pb-0">
            {/* Dot */}
            <div
              className={cn(
                'absolute left-0 w-3 h-3 rounded-full -translate-x-1/2 border-2 border-background',
                statusIndicator
              )}
            />

            {/* Content */}
            <div className="ml-4">
              <div className="flex items-center gap-2">
                <span className={cn('text-xs font-medium', typeStyle.color)}>
                  {typeStyle.label}
                </span>
                {showTimestamps && step.timestamp && (
                  <span className="text-xs text-muted-foreground">
                    {step.timestamp.toLocaleTimeString()}
                  </span>
                )}
              </div>
              <p className="text-sm font-medium">{step.title}</p>
              {step.content && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {step.content}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CompactView({ steps }: { steps: ReasoningStep[] }) {
  const flatSteps = flattenSteps(steps);
  const activeStep = flatSteps.find(s => s.status === 'active');
  const completedCount = flatSteps.filter(s => s.status === 'complete').length;

  return (
    <div className="space-y-2">
      {/* Progress bar */}
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all"
            style={{ width: `${(completedCount / flatSteps.length) * 100}%` }}
          />
        </div>
        <span className="text-xs text-muted-foreground">
          {completedCount}/{flatSteps.length}
        </span>
      </div>

      {/* Current step */}
      {activeStep && (
        <div className="flex items-center gap-2 text-sm">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-muted-foreground">
            {STEP_TYPE_STYLES[activeStep.type].label}:
          </span>
          <span className="font-medium truncate">{activeStep.title}</span>
        </div>
      )}
    </div>
  );
}

function flattenSteps(steps: ReasoningStep[]): ReasoningStep[] {
  return steps.reduce<ReasoningStep[]>((acc, step) => {
    acc.push(step);
    if (step.children) {
      acc.push(...flattenSteps(step.children));
    }
    return acc;
  }, []);
}

export function ReasoningPanel({
  steps,
  className,
  view = 'tree',
  showTimestamps = false,
  maxDepth = 10,
}: ReasoningPanelProps) {
  if (steps.length === 0) {
    return null;
  }

  return (
    <div className={cn('rounded-lg border bg-card p-3', className)}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium">Agent Reasoning</span>
        <span className="text-xs text-muted-foreground">
          {flattenSteps(steps).filter(s => s.status === 'complete').length}/{flattenSteps(steps).length} steps
        </span>
      </div>

      {view === 'tree' && (
        <div className="space-y-1">
          {steps.map((step) => (
            <TreeNode
              key={step.id}
              step={step}
              maxDepth={maxDepth}
              showTimestamps={showTimestamps}
            />
          ))}
        </div>
      )}

      {view === 'timeline' && (
        <TimelineView steps={flattenSteps(steps)} showTimestamps={showTimestamps} />
      )}

      {view === 'compact' && <CompactView steps={steps} />}
    </div>
  );
}

interface ThinkingIndicatorProps {
  isThinking: boolean;
  message?: string;
  className?: string;
}

export function ThinkingIndicator({ isThinking, message, className }: ThinkingIndicatorProps) {
  if (!isThinking) return null;

  return (
    <div className={cn('flex items-center gap-2 text-sm text-muted-foreground', className)}>
      <div className="flex gap-1">
        <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span>{message || 'Thinking...'}</span>
    </div>
  );
}
