/**
 * Run viewer component with real-time event streaming
 */

import { useCallback, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import {
  Play,
  Square,
  RotateCcw,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { runsApi } from '@/api/client'
import { useRunEventStream } from '@/hooks/use-sse'
import { cn } from '@/lib/utils'
import type { Run, RunEvent } from '@/types/api'

interface RunViewerProps {
  runId: string
}

const statusConfig: Record<Run['status'], { icon: React.ReactNode; color: string; label: string }> = {
  pending: {
    icon: <Clock className="h-5 w-5" />,
    color: 'text-yellow-500',
    label: 'Pending',
  },
  running: {
    icon: <Play className="h-5 w-5" />,
    color: 'text-blue-500',
    label: 'Running',
  },
  completed: {
    icon: <CheckCircle className="h-5 w-5" />,
    color: 'text-green-500',
    label: 'Completed',
  },
  failed: {
    icon: <XCircle className="h-5 w-5" />,
    color: 'text-red-500',
    label: 'Failed',
  },
  cancelled: {
    icon: <Square className="h-5 w-5" />,
    color: 'text-gray-500',
    label: 'Cancelled',
  },
}

function EventList({ events }: { events: RunEvent[] }) {
  return (
    <div className="space-y-2">
      {events.map((event) => (
        <div
          key={event.id}
          className="flex items-start gap-3 p-3 rounded-lg border bg-card"
        >
          <div className="flex-shrink-0">
            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-medium">
              {event.sequence_num}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium capitalize">
                {event.event_type.replace('_', ' ')}
              </span>
              <span className="text-xs text-muted-foreground">
                {format(new Date(event.timestamp), 'HH:mm:ss.SSS')}
              </span>
            </div>
            {event.payload && Object.keys(event.payload).length > 0 && (
              <pre className="mt-2 text-xs bg-muted p-2 rounded overflow-x-auto">
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            )}
            {event.duration_ms !== undefined && (
              <span className="inline-block mt-1 text-xs text-muted-foreground">
                Duration: {event.duration_ms}ms
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export function RunViewer({ runId }: RunViewerProps) {
  const [liveEvents, setLiveEvents] = useState<RunEvent[]>([])

  const { data: run, isLoading, error, refetch } = useQuery({
    queryKey: ['run', runId],
    queryFn: () => runsApi.get(runId),
    refetchInterval: (query) => {
      const data = query.state.data
      // Auto-refresh while running
      return data?.status === 'running' ? 2000 : false
    },
  })

  const { data: historicalEvents } = useQuery({
    queryKey: ['run-events', runId],
    queryFn: () => runsApi.getEvents(runId),
    enabled: !!run,
  })

  const handleEvent = useCallback((event: RunEvent) => {
    setLiveEvents((prev) => [...prev, event])
  }, [])

  const { status: sseStatus } = useRunEventStream(
    run?.status === 'running' ? runId : null,
    handleEvent
  )

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground">Loading run...</div>
      </div>
    )
  }

  if (error || !run) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-red-500">Failed to load run</div>
      </div>
    )
  }

  const config = statusConfig[run.status]
  const allEvents = [
    ...(historicalEvents || []),
    ...liveEvents.filter(
      (le) => !historicalEvents?.some((he) => he.id === le.id)
    ),
  ].sort((a, b) => a.sequence_num - b.sequence_num)

  return (
    <div className="h-full p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start gap-4">
            <div className={cn('mt-1', config.color)}>{config.icon}</div>
            <div>
              <h1 className="text-xl font-semibold">
                {run.run_type.charAt(0).toUpperCase() + run.run_type.slice(1)} Run
              </h1>
              <p className="text-sm text-muted-foreground font-mono mt-1">
                {run.id}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={cn('text-sm font-medium', config.color)}>
              {config.label}
            </span>
            {run.status === 'running' && sseStatus === 'connected' && (
              <span className="flex items-center gap-1 text-xs text-green-600">
                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                Live
              </span>
            )}
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {run.error_message && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">Error</span>
            </div>
            <p className="mt-2 text-sm text-red-600">{run.error_message}</p>
          </div>
        )}

        <Separator className="my-4" />

        {/* Metadata */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Type</p>
            <p className="text-sm font-medium capitalize">{run.run_type}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="text-sm font-medium">
              {format(new Date(run.created_at), 'PPpp')}
            </p>
          </div>
          {run.started_at && (
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Started</p>
              <p className="text-sm font-medium">
                {format(new Date(run.started_at), 'PPpp')}
              </p>
            </div>
          )}
          {run.completed_at && (
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-sm font-medium">
                {format(new Date(run.completed_at), 'PPpp')}
              </p>
            </div>
          )}
        </div>

        <Separator className="my-4" />

        {/* Tabs */}
        <Tabs defaultValue="events" className="mt-6">
          <TabsList>
            <TabsTrigger value="events">
              Events ({allEvents.length})
            </TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
            <TabsTrigger value="manifests">Manifests</TabsTrigger>
          </TabsList>

          <TabsContent value="events" className="mt-4">
            <ScrollArea className="h-[400px]">
              {allEvents.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No events recorded yet
                </div>
              ) : (
                <EventList events={allEvents} />
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="config" className="mt-4">
            <div className="rounded-lg border bg-muted/50 p-4">
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(run.config, null, 2)}
              </pre>
            </div>
          </TabsContent>

          <TabsContent value="manifests" className="mt-4">
            <div className="space-y-4">
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground mb-1">Input Manifest</p>
                <p className="text-sm font-mono">
                  {run.input_manifest_sha256 || 'None'}
                </p>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground mb-1">Output Manifest</p>
                <p className="text-sm font-mono">
                  {run.output_manifest_sha256 || 'None'}
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
