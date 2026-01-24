/**
 * Timeline panel - shows run events in real-time
 */

import { useCallback, useRef, useEffect } from 'react'
import { format } from 'date-fns'
import {
  Play,
  CheckCircle,
  XCircle,
  Wrench,
  MessageSquare,
  Search,
  Save,
  AlertTriangle,
  FileBox,
  GitBranch,
  Circle,
} from 'lucide-react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useWorkbenchStore } from '@/stores/workbench-store'
import { useRunEventStream } from '@/hooks/use-sse'

const eventIcons: Record<string, React.ReactNode> = {
  // Lifecycle
  run_started: <Play className="h-4 w-4 text-blue-500" />,
  run_paused: <Circle className="h-4 w-4 text-orange-500" />,
  run_resumed: <Play className="h-4 w-4 text-blue-500" />,
  run_completed: <CheckCircle className="h-4 w-4 text-green-500" />,
  run_failed: <XCircle className="h-4 w-4 text-red-500" />,
  run_cancelled: <XCircle className="h-4 w-4 text-gray-500" />,

  // Steps
  step_started: <Play className="h-4 w-4 text-blue-500" />,
  step_completed: <CheckCircle className="h-4 w-4 text-green-500" />,

  // Tool calls
  tool_call_started: <Wrench className="h-4 w-4 text-purple-500" />,
  tool_call_completed: <Wrench className="h-4 w-4 text-purple-500" />,

  // LLM
  llm_request: <MessageSquare className="h-4 w-4 text-orange-500" />,
  llm_response: <MessageSquare className="h-4 w-4 text-orange-500" />,

  // Retrieval
  retrieval_query: <Search className="h-4 w-4 text-cyan-500" />,
  retrieval_result: <Search className="h-4 w-4 text-cyan-500" />,

  // Substrate
  artifact_emitted: <FileBox className="h-4 w-4 text-emerald-500" />,
  manifest_created: <FileBox className="h-4 w-4 text-emerald-500" />,
  pointer_moved: <GitBranch className="h-4 w-4 text-emerald-500" />,

  // State / errors
  checkpoint: <Save className="h-4 w-4 text-cyan-500" />,
  error: <XCircle className="h-4 w-4 text-red-500" />,
  warning: <AlertTriangle className="h-4 w-4 text-yellow-600" />,
}

const eventLabels: Record<string, string> = {
  run_started: 'Run Started',
  run_paused: 'Run Paused',
  run_resumed: 'Run Resumed',
  run_completed: 'Run Completed',
  run_failed: 'Run Failed',
  run_cancelled: 'Run Cancelled',
  step_started: 'Step Started',
  step_completed: 'Step Completed',
  tool_call_started: 'Tool Call Started',
  tool_call_completed: 'Tool Call Completed',
  llm_request: 'LLM Request',
  llm_response: 'LLM Response',
  retrieval_query: 'Retrieval Query',
  retrieval_result: 'Retrieval Result',
  artifact_emitted: 'Artifact Emitted',
  manifest_created: 'Manifest Created',
  pointer_moved: 'Pointer Moved',
  checkpoint: 'Checkpoint',
  error: 'Error',
  warning: 'Warning',
}

interface EventCardProps {
  event: {
    id: number
    run_id: string
    event_type: string
    payload: Record<string, unknown>
    timestamp: string
    duration_ms?: number
    sequence_num: number
  }
}

function EventCard({ event }: EventCardProps) {
  const icon = eventIcons[event.event_type] || (
    <Circle className="h-4 w-4" />
  )
  const label =
    eventLabels[event.event_type] || event.event_type.replace(/_/g, ' ')

  const stepName = event.payload.step_name
  const toolName = event.payload.tool_name
  const errorValue = event.payload.error
  const errorText =
    typeof errorValue === 'string'
      ? errorValue
      : errorValue
        ? JSON.stringify(errorValue)
        : null

  return (
    <div className="flex gap-3 p-3 hover:bg-muted/50 rounded-md">
      <div className="flex-shrink-0 mt-0.5">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="text-sm font-medium">{label}</span>
          <span className="text-xs text-muted-foreground">
            {format(new Date(event.timestamp), 'HH:mm:ss.SSS')}
          </span>
        </div>
        {event.payload && Object.keys(event.payload).length > 0 && (
          <div className="mt-1 text-xs text-muted-foreground">
            {typeof stepName === 'string' && (
              <span className="inline-block bg-muted px-1.5 py-0.5 rounded mr-2">
                {stepName}
              </span>
            )}
            {typeof toolName === 'string' && (
              <span className="inline-block bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded mr-2">
                {toolName}
              </span>
            )}
            {event.duration_ms !== undefined && (
              <span className="inline-block bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">
                {event.duration_ms}ms
              </span>
            )}
          </div>
        )}
        {errorText && (
          <div className="mt-1 text-xs text-red-600 bg-red-50 p-1.5 rounded">
            {errorText}
          </div>
        )}
      </div>
    </div>
  )
}

export function TimelinePanel() {
  const { selectedRunId } = useWorkbenchStore()
  const scrollRef = useRef<HTMLDivElement>(null)

  const handleEvent = useCallback(() => {
    // Auto-scroll to bottom on new events
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [])

  const { events, status } = useRunEventStream(selectedRunId, handleEvent)

  // Auto-scroll effect
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [events])

  const getStatusIndicator = () => {
    switch (status) {
      case 'connected':
        return (
          <div className="flex items-center gap-1.5 text-xs text-green-600">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            Live
          </div>
        )
      case 'connecting':
        return (
          <div className="flex items-center gap-1.5 text-xs text-yellow-600">
            <div className="h-2 w-2 rounded-full bg-yellow-500" />
            Connecting...
          </div>
        )
      case 'error':
        return (
          <div className="flex items-center gap-1.5 text-xs text-red-600">
            <AlertTriangle className="h-3 w-3" />
            Error
          </div>
        )
      default:
        return (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <div className="h-2 w-2 rounded-full bg-gray-400" />
            Disconnected
          </div>
        )
    }
  }

  return (
    <div className="flex h-full flex-col border-t bg-background">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold">Timeline</h2>
          {selectedRunId && (
            <span className="text-xs text-muted-foreground font-mono">
              {selectedRunId.slice(0, 8)}
            </span>
          )}
        </div>
        {selectedRunId && getStatusIndicator()}
      </div>

      {!selectedRunId ? (
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
          Select a run to view its timeline
        </div>
      ) : events.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
          {status === 'connected' ? 'Waiting for events...' : 'No events yet'}
        </div>
      ) : (
        <ScrollArea className="flex-1" ref={scrollRef}>
          <div className="p-2 space-y-1">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  )
}
