/**
 * Run timeline component for displaying run events in the chat panel.
 *
 * Shows tool calls, timing, and token usage in a compact collapsible format.
 */

import { useCallback, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import {
  ChevronDown,
  ChevronRight,
  Clock,
  Wrench,
  MessageSquare,
  Search,
  AlertCircle,
  CheckCircle,
  Loader2,
  Zap,
} from 'lucide-react'

import { runsApi } from '@/api/client'
import { useRunEventStream } from '@/hooks/use-sse'
import { cn } from '@/lib/utils'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import type { RunEvent } from '@/types/api'

interface RunTimelineProps {
  runId: string
  className?: string
}

/**
 * Event type configuration for icons and colors.
 */
const eventTypeConfig: Record<
  string,
  { icon: React.ElementType; color: string; label: string }
> = {
  run_started: { icon: Zap, color: 'text-blue-500', label: 'Run Started' },
  run_completed: { icon: CheckCircle, color: 'text-green-500', label: 'Completed' },
  run_failed: { icon: AlertCircle, color: 'text-red-500', label: 'Failed' },
  step_started: { icon: ChevronRight, color: 'text-gray-500', label: 'Step' },
  step_completed: { icon: CheckCircle, color: 'text-gray-500', label: 'Step Done' },
  tool_call_started: { icon: Wrench, color: 'text-purple-500', label: 'Tool Call' },
  tool_call_completed: { icon: Wrench, color: 'text-purple-500', label: 'Tool Result' },
  llm_request: { icon: MessageSquare, color: 'text-blue-500', label: 'LLM Request' },
  llm_response: { icon: MessageSquare, color: 'text-blue-500', label: 'LLM Response' },
  retrieval_query: { icon: Search, color: 'text-orange-500', label: 'RAG Query' },
  retrieval_result: { icon: Search, color: 'text-orange-500', label: 'RAG Result' },
  error: { icon: AlertCircle, color: 'text-red-500', label: 'Error' },
  warning: { icon: AlertCircle, color: 'text-yellow-500', label: 'Warning' },
}

const defaultEventConfig = { icon: Clock, color: 'text-gray-400', label: 'Event' }

/**
 * Individual timeline event row.
 */
function TimelineEvent({ event, isLast }: { event: RunEvent; isLast: boolean }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const config = eventTypeConfig[event.event_type] ?? defaultEventConfig
  const Icon = config.icon

  const hasPayload = event.payload && Object.keys(event.payload).length > 0

  // Extract key info from payload for compact display
  const toolName = event.payload?.tool_name as string | undefined
  const stepName = event.payload?.step_name as string | undefined
  const model = event.payload?.model as string | undefined

  const displayLabel = toolName ?? stepName ?? model ?? config.label

  return (
    <div className="relative flex gap-3 pb-3">
      {/* Timeline connector line */}
      {!isLast && (
        <div className="absolute left-[11px] top-6 bottom-0 w-px bg-border" />
      )}

      {/* Icon */}
      <div
        className={cn(
          'flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted',
          config.color
        )}
      >
        <Icon className="h-3 w-3" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
          <div className="flex items-center justify-between gap-2">
            <CollapsibleTrigger
              className="flex items-center gap-1 text-sm font-medium hover:underline disabled:opacity-50"
              disabled={!hasPayload}
            >
              {hasPayload && (
                <span className="text-muted-foreground">
                  {isExpanded ? (
                    <ChevronDown className="h-3 w-3" />
                  ) : (
                    <ChevronRight className="h-3 w-3" />
                  )}
                </span>
              )}
              <span className="truncate">{displayLabel}</span>
            </CollapsibleTrigger>

            <div className="flex items-center gap-2 text-xs text-muted-foreground shrink-0">
              {event.duration_ms !== undefined && event.duration_ms > 0 && (
                <span className="tabular-nums">{event.duration_ms}ms</span>
              )}
              <span className="tabular-nums">
                {format(new Date(event.timestamp), 'HH:mm:ss')}
              </span>
            </div>
          </div>

          {hasPayload && (
            <CollapsibleContent>
              <pre className="mt-2 p-2 text-xs bg-muted rounded overflow-x-auto max-h-40">
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            </CollapsibleContent>
          )}
        </Collapsible>
      </div>
    </div>
  )
}

function summarizeTokenUsage(tokenUsage: Record<string, unknown> | undefined) {
  const totals = { inputTokens: 0, outputTokens: 0, costMicros: 0 }
  if (!tokenUsage) {
    return totals
  }

  for (const usage of Object.values(tokenUsage)) {
    if (!usage || typeof usage !== 'object') continue
    const record = usage as Record<string, unknown>
    totals.inputTokens += Number(record.input_tokens ?? record.input ?? 0)
    totals.outputTokens += Number(record.output_tokens ?? record.output ?? 0)
    totals.costMicros += Number(record.cost_micros ?? 0)
  }

  return totals
}

function formatCost(costMicros: number): string {
  const usd = costMicros / 1_000_000
  if (usd === 0) return '$0.00'
  if (usd >= 0.01) return `$${usd.toFixed(4)}`
  return `$${usd.toFixed(6)}`.replace(/0+$/, '').replace(/\.$/, '')
}

/**
 * Summary stats displayed at the top of the timeline.
 */
function TimelineSummary({
  events,
  isLive,
  tokenUsage,
}: {
  events: RunEvent[]
  isLive: boolean
  tokenUsage?: Record<string, unknown>
}) {
  const toolCalls = events.filter((e) => e.event_type === 'tool_call_started').length
  const llmCalls = events.filter((e) => e.event_type === 'llm_request').length
  const totalDuration = events.reduce((acc, e) => acc + (e.duration_ms ?? 0), 0)
  const hasError = events.some((e) => e.event_type === 'error' || e.event_type === 'run_failed')
  const usage = summarizeTokenUsage(tokenUsage)

  return (
    <div className="flex items-center gap-4 text-xs text-muted-foreground pb-3 border-b mb-3">
      {isLive && (
        <span className="flex items-center gap-1 text-green-600">
          <Loader2 className="h-3 w-3 animate-spin" />
          Live
        </span>
      )}
      {toolCalls > 0 && (
        <span className="flex items-center gap-1">
          <Wrench className="h-3 w-3" />
          {toolCalls} tool{toolCalls !== 1 ? 's' : ''}
        </span>
      )}
      {llmCalls > 0 && (
        <span className="flex items-center gap-1">
          <MessageSquare className="h-3 w-3" />
          {llmCalls} LLM call{llmCalls !== 1 ? 's' : ''}
        </span>
      )}
      {(usage.inputTokens > 0 || usage.outputTokens > 0) && (
        <span className="flex items-center gap-1">
          <MessageSquare className="h-3 w-3" />
          {usage.inputTokens.toLocaleString()} in · {usage.outputTokens.toLocaleString()} out
        </span>
      )}
      {usage.costMicros > 0 && (
        <span className="flex items-center gap-1">
          <Zap className="h-3 w-3" />
          {formatCost(usage.costMicros)}
        </span>
      )}
      {totalDuration > 0 && (
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {totalDuration >= 1000
            ? `${(totalDuration / 1000).toFixed(1)}s`
            : `${totalDuration}ms`}
        </span>
      )}
      {hasError && (
        <span className="flex items-center gap-1 text-red-500">
          <AlertCircle className="h-3 w-3" />
          Error
        </span>
      )}
    </div>
  )
}

export function RunTimeline({ runId, className }: RunTimelineProps) {
  const [liveEvents, setLiveEvents] = useState<RunEvent[]>([])

  // Fetch run to check status
  const { data: run } = useQuery({
    queryKey: ['run', runId],
    queryFn: () => runsApi.get(runId),
    refetchInterval: (query) => {
      const data = query.state.data
      return data?.status === 'running' ? 2000 : false
    },
  })

  // Fetch historical events
  const { data: historicalEvents, isLoading } = useQuery({
    queryKey: ['run-events', runId],
    queryFn: () => runsApi.getEvents(runId),
    enabled: !!runId,
  })

  // Handle live events from SSE
  const handleEvent = useCallback((event: RunEvent) => {
    setLiveEvents((prev) => [...prev, event])
  }, [])

  const { status: sseStatus } = useRunEventStream(
    run?.status === 'running' ? runId : null,
    handleEvent
  )

  const isLive = run?.status === 'running' && sseStatus === 'connected'

  // Merge and dedupe events
  const allEvents = [
    ...(historicalEvents || []),
    ...liveEvents.filter((le) => !historicalEvents?.some((he) => he.id === le.id)),
  ].sort((a, b) => a.sequence_num - b.sequence_num)

  // Filter to show only interesting events (skip noisy ones)
  const visibleEvents = allEvents.filter((e) =>
    [
      'run_started',
      'run_completed',
      'run_failed',
      'tool_call_started',
      'tool_call_completed',
      'llm_request',
      'llm_response',
      'retrieval_query',
      'retrieval_result',
      'error',
      'warning',
    ].includes(e.event_type)
  )

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center py-8', className)}>
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (visibleEvents.length === 0) {
    return (
      <div className={cn('text-center text-sm text-muted-foreground py-8', className)}>
        No events recorded yet
      </div>
    )
  }

  return (
    <div className={cn('p-4', className)}>
      <TimelineSummary events={allEvents} isLive={isLive} tokenUsage={run?.token_usage} />
      <ScrollArea className="max-h-[400px]">
        <div className="pr-4">
          {visibleEvents.map((event, index) => (
            <TimelineEvent
              key={event.id}
              event={event}
              isLast={index === visibleEvents.length - 1}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
