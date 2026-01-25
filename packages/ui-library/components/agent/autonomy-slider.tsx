/**
 * Autonomy Slider Component
 *
 * Based on Cursor's autonomy pattern: allows users to control how much
 * independence to give the AI agent, from suggestions to full autonomy.
 *
 * Key learnings applied:
 * - Progressive trust building
 * - Per-task configurable autonomy
 * - Clear visual feedback of current level
 */

import * as React from 'react';
import { createContext, useContext, useState, useCallback } from 'react';
import { cn } from '../../lib/utils';

export type AutonomyLevel =
  | 'suggestions'     // AI suggests, user executes
  | 'assisted'        // AI executes with confirmation
  | 'supervised'      // AI executes, user can intervene
  | 'autonomous';     // AI executes freely (within guardrails)

interface AutonomyContextValue {
  level: AutonomyLevel;
  setLevel: (level: AutonomyLevel) => void;
  canExecute: (actionType: ActionType) => boolean;
  requiresApproval: (actionType: ActionType) => boolean;
}

type ActionType =
  | 'read'
  | 'analyze'
  | 'modify'
  | 'external'
  | 'compliance';

const AutonomyContext = createContext<AutonomyContextValue | null>(null);

export function useAutonomyContext() {
  const context = useContext(AutonomyContext);
  if (!context) {
    throw new Error('useAutonomyContext must be used within AutonomyProvider');
  }
  return context;
}

interface AutonomyProviderProps {
  children: React.ReactNode;
  defaultLevel?: AutonomyLevel;
  onLevelChange?: (level: AutonomyLevel) => void;
}

// Permission matrix based on research findings
const AUTONOMY_PERMISSIONS: Record<AutonomyLevel, Record<ActionType, { canExecute: boolean; requiresApproval: boolean }>> = {
  suggestions: {
    read: { canExecute: true, requiresApproval: false },
    analyze: { canExecute: false, requiresApproval: true },
    modify: { canExecute: false, requiresApproval: true },
    external: { canExecute: false, requiresApproval: true },
    compliance: { canExecute: false, requiresApproval: true },
  },
  assisted: {
    read: { canExecute: true, requiresApproval: false },
    analyze: { canExecute: true, requiresApproval: false },
    modify: { canExecute: true, requiresApproval: true },
    external: { canExecute: false, requiresApproval: true },
    compliance: { canExecute: false, requiresApproval: true },
  },
  supervised: {
    read: { canExecute: true, requiresApproval: false },
    analyze: { canExecute: true, requiresApproval: false },
    modify: { canExecute: true, requiresApproval: false },
    external: { canExecute: true, requiresApproval: true },
    compliance: { canExecute: false, requiresApproval: true },
  },
  autonomous: {
    read: { canExecute: true, requiresApproval: false },
    analyze: { canExecute: true, requiresApproval: false },
    modify: { canExecute: true, requiresApproval: false },
    external: { canExecute: true, requiresApproval: false },
    compliance: { canExecute: false, requiresApproval: true }, // Always requires human for compliance
  },
};

export function AutonomyProvider({ children, defaultLevel = 'assisted', onLevelChange }: AutonomyProviderProps) {
  const [level, setLevelState] = useState<AutonomyLevel>(defaultLevel);

  const setLevel = useCallback((newLevel: AutonomyLevel) => {
    setLevelState(newLevel);
    onLevelChange?.(newLevel);
  }, [onLevelChange]);

  const canExecute = useCallback((actionType: ActionType) => {
    return AUTONOMY_PERMISSIONS[level][actionType].canExecute;
  }, [level]);

  const requiresApproval = useCallback((actionType: ActionType) => {
    return AUTONOMY_PERMISSIONS[level][actionType].requiresApproval;
  }, [level]);

  return (
    <AutonomyContext.Provider value={{ level, setLevel, canExecute, requiresApproval }}>
      {children}
    </AutonomyContext.Provider>
  );
}

interface AutonomySliderProps {
  className?: string;
  showLabels?: boolean;
  showDescription?: boolean;
  disabled?: boolean;
}

const LEVEL_CONFIG: Record<AutonomyLevel, { label: string; description: string; color: string }> = {
  suggestions: {
    label: 'Suggestions',
    description: 'AI suggests actions, you execute them',
    color: 'bg-blue-500',
  },
  assisted: {
    label: 'Assisted',
    description: 'AI executes with your confirmation',
    color: 'bg-green-500',
  },
  supervised: {
    label: 'Supervised',
    description: 'AI executes, you can intervene anytime',
    color: 'bg-yellow-500',
  },
  autonomous: {
    label: 'Autonomous',
    description: 'AI works independently within guardrails',
    color: 'bg-orange-500',
  },
};

const LEVELS: AutonomyLevel[] = ['suggestions', 'assisted', 'supervised', 'autonomous'];

export function AutonomySlider({
  className,
  showLabels = true,
  showDescription = true,
  disabled = false
}: AutonomySliderProps) {
  const { level, setLevel } = useAutonomyContext();
  const currentIndex = LEVELS.indexOf(level);
  const config = LEVEL_CONFIG[level];

  return (
    <div className={cn('space-y-3', className)}>
      {showLabels && (
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">{config.label}</span>
          <span className={cn('h-2 w-2 rounded-full', config.color)} />
        </div>
      )}

      <div className="relative">
        {/* Track */}
        <div className="h-2 bg-muted rounded-full">
          {/* Fill */}
          <div
            className={cn('h-full rounded-full transition-all', config.color)}
            style={{ width: `${((currentIndex + 1) / LEVELS.length) * 100}%` }}
          />
        </div>

        {/* Buttons */}
        <div className="absolute inset-0 flex items-center justify-between">
          {LEVELS.map((l, index) => (
            <button
              key={l}
              onClick={() => !disabled && setLevel(l)}
              disabled={disabled}
              className={cn(
                'w-4 h-4 rounded-full border-2 transition-all',
                'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
                index <= currentIndex
                  ? cn('border-transparent', config.color)
                  : 'border-muted-foreground/30 bg-background',
                disabled && 'cursor-not-allowed opacity-50'
              )}
              title={LEVEL_CONFIG[l].label}
            />
          ))}
        </div>
      </div>

      {showDescription && (
        <p className="text-xs text-muted-foreground">{config.description}</p>
      )}
    </div>
  );
}
