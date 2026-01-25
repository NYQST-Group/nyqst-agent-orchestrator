/**
 * Trust Indicator Component
 *
 * Based on research findings:
 * - Trust calibration through demonstrated reliability
 * - Progressive autonomy building
 * - Visual feedback of agent confidence and track record
 */

import * as React from 'react';
import { cn } from '../../lib/utils';

export type TrustLevel = 'new' | 'learning' | 'reliable' | 'trusted' | 'expert';

interface TrustIndicatorProps {
  level: TrustLevel;
  score?: number; // 0-100
  stats?: {
    totalActions: number;
    successfulActions: number;
    rejectedActions: number;
    lastActionAt?: Date;
  };
  className?: string;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const TRUST_LEVELS: Record<TrustLevel, { label: string; description: string; color: string; minScore: number }> = {
  new: {
    label: 'New',
    description: 'Agent is new, all actions require approval',
    color: 'text-muted-foreground',
    minScore: 0,
  },
  learning: {
    label: 'Learning',
    description: 'Agent is learning your preferences',
    color: 'text-blue-500',
    minScore: 20,
  },
  reliable: {
    label: 'Reliable',
    description: 'Agent has demonstrated consistency',
    color: 'text-green-500',
    minScore: 50,
  },
  trusted: {
    label: 'Trusted',
    description: 'Agent can work with minimal oversight',
    color: 'text-emerald-500',
    minScore: 75,
  },
  expert: {
    label: 'Expert',
    description: 'Agent has proven expertise in this domain',
    color: 'text-purple-500',
    minScore: 90,
  },
};

export function getTrustLevelFromScore(score: number): TrustLevel {
  if (score >= 90) return 'expert';
  if (score >= 75) return 'trusted';
  if (score >= 50) return 'reliable';
  if (score >= 20) return 'learning';
  return 'new';
}

export function TrustIndicator({
  level,
  score,
  stats,
  className,
  showDetails = false,
  size = 'md',
}: TrustIndicatorProps) {
  const config = TRUST_LEVELS[level];
  const displayScore = score ?? config.minScore;
  const successRate = stats
    ? Math.round((stats.successfulActions / Math.max(stats.totalActions, 1)) * 100)
    : null;

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  return (
    <div className={cn('space-y-2', sizeClasses[size], className)}>
      {/* Main indicator */}
      <div className="flex items-center gap-2">
        {/* Trust badge */}
        <div className={cn(
          'flex items-center gap-1.5 px-2 py-1 rounded-full bg-muted',
          config.color
        )}>
          <TrustIcon level={level} className={cn(
            size === 'sm' && 'w-3 h-3',
            size === 'md' && 'w-4 h-4',
            size === 'lg' && 'w-5 h-5',
          )} />
          <span className="font-medium">{config.label}</span>
        </div>

        {/* Score */}
        {score !== undefined && (
          <span className="text-muted-foreground">{displayScore}%</span>
        )}
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all',
            level === 'new' && 'bg-muted-foreground',
            level === 'learning' && 'bg-blue-500',
            level === 'reliable' && 'bg-green-500',
            level === 'trusted' && 'bg-emerald-500',
            level === 'expert' && 'bg-purple-500',
          )}
          style={{ width: `${displayScore}%` }}
        />
      </div>

      {/* Details */}
      {showDetails && (
        <div className="space-y-1.5">
          <p className="text-muted-foreground">{config.description}</p>

          {stats && (
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <span>{stats.totalActions} actions</span>
              {successRate !== null && (
                <span>{successRate}% success rate</span>
              )}
              {stats.rejectedActions > 0 && (
                <span>{stats.rejectedActions} rejected</span>
              )}
              {stats.lastActionAt && (
                <span>Last: {formatRelativeTime(stats.lastActionAt)}</span>
              )}
            </div>
          )}

          {/* Trust level milestones */}
          <div className="flex items-center justify-between text-xs text-muted-foreground pt-1">
            {Object.entries(TRUST_LEVELS).map(([key, value]) => (
              <div
                key={key}
                className={cn(
                  'flex flex-col items-center',
                  displayScore >= value.minScore && value.color
                )}
              >
                <span className="font-medium">{value.minScore}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TrustIcon({ level, className }: { level: TrustLevel; className?: string }) {
  // Simple icon representations
  const icons: Record<TrustLevel, React.ReactNode> = {
    new: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 8v4M12 16h.01" />
      </svg>
    ),
    learning: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
      </svg>
    ),
    reliable: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    ),
    trusted: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <polyline points="9 12 11 14 15 10" />
      </svg>
    ),
    expert: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
  };

  return icons[level];
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}
