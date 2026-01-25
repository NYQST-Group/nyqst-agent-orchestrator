import { useState, useMemo } from 'react';
import {
  Play,
  Pause,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  ChevronRight,
  ChevronDown,
  Wrench,
  Search as SearchIcon,
  FileText,
  GitBranch,
  RefreshCw,
} from 'lucide-react';
import { cn, formatRelativeTime } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { TimelineSkeleton } from '@/components/async/loading-states';
import { AsyncBoundary } from '@/components/async/suspense-wrapper';
import type { Run, RunStatus, RunLedgerEvent } from '@/types';

interface RunExplorerPaneProps {
  paneId: string;
}

// Mock data
const MOCK_RUNS: Run[] = [
  {
    id: 'run-1',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'agentic',
    status: 'completed',
    inputManifestIds: ['manifest-1'],
    outputManifestId: 'manifest-2',
    checkpoints: [],
    startedAt: new Date(Date.now() - 600000).toISOString(),
    completedAt: new Date(Date.now() - 300000).toISOString(),
    usage: { totalTokens: 5420, promptTokens: 4200, completionTokens: 1220, toolCalls: 8, retrievalQueries: 3, durationMs: 300000 },
    metadata: { name: 'Document Analysis' },
    createdAt: new Date(Date.now() - 600000).toISOString(),
    updatedAt: new Date(Date.now() - 300000).toISOString(),
  },
  {
    id: 'run-2',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'agentic',
    status: 'running',
    inputManifestIds: ['manifest-3'],
    checkpoints: [{ id: 'cp-1', stepIndex: 3, createdAt: new Date().toISOString(), state: {} }],
    startedAt: new Date(Date.now() - 120000).toISOString(),
    usage: { totalTokens: 2100, promptTokens: 1800, completionTokens: 300, toolCalls: 4, retrievalQueries: 2, durationMs: 120000 },
    metadata: { name: 'Compliance Check' },
    createdAt: new Date(Date.now() - 120000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'run-3',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'deterministic',
    status: 'failed',
    inputManifestIds: ['manifest-4'],
    checkpoints: [],
    startedAt: new Date(Date.now() - 3600000).toISOString(),
    completedAt: new Date(Date.now() - 3500000).toISOString(),
    error: { code: 'TIMEOUT', message: 'Run exceeded maximum duration' },
    metadata: { name: 'KB Index Build' },
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date(Date.now() - 3500000).toISOString(),
  },
];

const MOCK_EVENTS: RunLedgerEvent[] = [
  {
    id: 'evt-1',
    type: 'tool.call.started',
    category: 'tooling',
    timestamp: new Date(Date.now() - 590000).toISOString(),
    runId: 'run-1',
    principalId: 'agent-1',
    visibility: 'public',
    payload: { toolCallId: 'tc-1', toolName: 'kb_query', toolVersion: '1.0.0', argsHash: 'abc123', args: { query: 'compliance requirements' } },
  },
  {
    id: 'evt-2',
    type: 'tool.call.completed',
    category: 'tooling',
    timestamp: new Date(Date.now() - 580000).toISOString(),
    runId: 'run-1',
    principalId: 'agent-1',
    visibility: 'public',
    payload: { toolCallId: 'tc-1', toolName: 'kb_query', success: true, durationMs: 10000, outputArtifactIds: ['art-1'] },
  },
  {
    id: 'evt-3',
    type: 'artifact.emitted',
    category: 'artifact',
    timestamp: new Date(Date.now() - 550000).toISOString(),
    runId: 'run-1',
    principalId: 'agent-1',
    visibility: 'public',
    payload: { artifactId: 'art-2', contentHash: 'hash123', logicalType: 'claim_set', mimeType: 'application/json', sizeBytes: 4520 },
  },
] as RunLedgerEvent[];

const STATUS_CONFIG: Record<RunStatus, { icon: React.ElementType; color: string; label: string }> = {
  pending: { icon: Clock, color: 'text-muted-foreground', label: 'Pending' },
  running: { icon: Play, color: 'text-blue-500', label: 'Running' },
  completed: { icon: CheckCircle, color: 'text-green-500', label: 'Completed' },
  failed: { icon: XCircle, color: 'text-red-500', label: 'Failed' },
  cancelled: { icon: AlertCircle, color: 'text-yellow-500', label: 'Cancelled' },
  paused: { icon: Pause, color: 'text-orange-500', label: 'Paused' },
};

export function RunExplorerPane({ paneId }: RunExplorerPaneProps) {
  const [selectedRunId, setSelectedRunId] = useState<string | null>('run-1');
  const [search, setSearch] = useState('');
  const [expandedRuns, setExpandedRuns] = useState<Set<string>>(new Set(['run-1']));

  const filteredRuns = useMemo(() => {
    if (!search) return MOCK_RUNS;
    const lower = search.toLowerCase();
    return MOCK_RUNS.filter(
      (run) =>
        run.id.toLowerCase().includes(lower) ||
        (run.metadata.name as string)?.toLowerCase().includes(lower) ||
        run.status.toLowerCase().includes(lower)
    );
  }, [search]);

  const selectedRun = useMemo(
    () => MOCK_RUNS.find((r) => r.id === selectedRunId),
    [selectedRunId]
  );

  const toggleExpanded = (runId: string) => {
    setExpandedRuns((prev) => {
      const next = new Set(prev);
      if (next.has(runId)) {
        next.delete(runId);
      } else {
        next.add(runId);
      }
      return next;
    });
  };

  return (
    <div className="h-full flex">
      {/* Run list */}
      <div className="w-72 border-r flex flex-col">
        <div className="p-3 border-b">
          <div className="relative">
            <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search runs..."
              className="pl-8 h-9"
            />
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {filteredRuns.map((run) => {
              const status = STATUS_CONFIG[run.status];
              const StatusIcon = status.icon;
              const isSelected = run.id === selectedRunId;
              const isExpanded = expandedRuns.has(run.id);

              return (
                <div key={run.id}>
                  <button
                    className={cn(
                      'w-full flex items-center gap-2 p-2 rounded-md text-left transition-colors',
                      isSelected ? 'bg-accent' : 'hover:bg-muted/50'
                    )}
                    onClick={() => setSelectedRunId(run.id)}
                  >
                    <button
                      className="p-0.5 hover:bg-muted rounded"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleExpanded(run.id);
                      }}
                    >
                      {isExpanded ? (
                        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                      )}
                    </button>

                    <StatusIcon className={cn('h-4 w-4 shrink-0', status.color)} />

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {(run.metadata.name as string) || run.id}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatRelativeTime(run.startedAt || run.createdAt)}
                      </p>
                    </div>

                    <Badge variant="outline" className="text-xs shrink-0">
                      {run.type}
                    </Badge>
                  </button>

                  {/* Expanded run steps preview */}
                  {isExpanded && (
                    <div className="ml-8 pl-2 border-l space-y-1 py-1">
                      <RunEventPreview runId={run.id} events={MOCK_EVENTS.filter(e => e.runId === run.id)} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </ScrollArea>

        <div className="p-2 border-t">
          <Button variant="outline" size="sm" className="w-full gap-2">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Run detail */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <AsyncBoundary loadingFallback={<TimelineSkeleton />}>
          {selectedRun ? (
            <RunDetail run={selectedRun} events={MOCK_EVENTS} />
          ) : (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <p>Select a run to view details</p>
            </div>
          )}
        </AsyncBoundary>
      </div>
    </div>
  );
}

function RunEventPreview({ runId, events }: { runId: string; events: RunLedgerEvent[] }) {
  const runEvents = events.slice(0, 3);

  if (runEvents.length === 0) {
    return <p className="text-xs text-muted-foreground py-1">No events</p>;
  }

  return (
    <>
      {runEvents.map((event) => (
        <div key={event.id} className="flex items-center gap-2 py-0.5">
          {event.type.startsWith('tool') ? (
            <Wrench className="h-3 w-3 text-muted-foreground" />
          ) : event.type.startsWith('artifact') ? (
            <FileText className="h-3 w-3 text-muted-foreground" />
          ) : (
            <GitBranch className="h-3 w-3 text-muted-foreground" />
          )}
          <span className="text-xs text-muted-foreground truncate">
            {event.type.split('.').pop()}
          </span>
        </div>
      ))}
      {events.length > 3 && (
        <p className="text-xs text-muted-foreground">+{events.length - 3} more</p>
      )}
    </>
  );
}

function RunDetail({ run, events }: { run: Run; events: RunLedgerEvent[] }) {
  const status = STATUS_CONFIG[run.status];
  const StatusIcon = status.icon;
  const runEvents = events.filter((e) => e.runId === run.id);

  return (
    <>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              {(run.metadata.name as string) || run.id}
            </h2>
            <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <StatusIcon className={cn('h-4 w-4', status.color)} />
                {status.label}
              </span>
              <span>{run.type}</span>
              {run.startedAt && (
                <span>Started {formatRelativeTime(run.startedAt)}</span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {run.status === 'running' && (
              <Button variant="destructive" size="sm">
                Stop
              </Button>
            )}
            {run.status === 'failed' && (
              <Button variant="outline" size="sm">
                Retry
              </Button>
            )}
          </div>
        </div>

        {/* Usage stats */}
        {run.usage && (
          <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
            <span>{run.usage.totalTokens.toLocaleString()} tokens</span>
            <span>{run.usage.toolCalls} tool calls</span>
            <span>{run.usage.retrievalQueries} queries</span>
            <span>{Math.round(run.usage.durationMs / 1000)}s duration</span>
          </div>
        )}

        {/* Error */}
        {run.error && (
          <div className="mt-3 p-2 rounded-md bg-destructive/10 text-destructive text-sm">
            <p className="font-medium">{run.error.code}</p>
            <p className="text-xs">{run.error.message}</p>
          </div>
        )}
      </div>

      {/* Timeline */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {runEvents.map((event, index) => (
            <TimelineEvent key={event.id} event={event} isLast={index === runEvents.length - 1} />
          ))}
          {runEvents.length === 0 && (
            <p className="text-center text-muted-foreground py-8">
              No events recorded for this run
            </p>
          )}
        </div>
      </ScrollArea>
    </>
  );
}

function TimelineEvent({ event, isLast }: { event: RunLedgerEvent; isLast: boolean }) {
  const getEventIcon = (type: string) => {
    if (type.startsWith('tool')) return Wrench;
    if (type.startsWith('artifact')) return FileText;
    if (type.startsWith('retrieval')) return SearchIcon;
    return GitBranch;
  };

  const Icon = getEventIcon(event.type);

  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
        {!isLast && <div className="w-px flex-1 bg-border mt-2" />}
      </div>

      <div className="flex-1 pb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{event.type}</span>
          <span className="text-xs text-muted-foreground">
            {formatRelativeTime(event.timestamp)}
          </span>
        </div>

        <div className="mt-1 p-2 rounded-md bg-muted text-sm">
          <pre className="text-xs overflow-auto whitespace-pre-wrap">
            {JSON.stringify(event.payload, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
