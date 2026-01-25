import { useState, useMemo, useCallback } from 'react';
import {
  Search,
  Filter,
  Grid,
  List,
  FileText,
  FileJson,
  Table,
  Image,
  File,
  Download,
  Eye,
  Pin,
  MoreHorizontal,
  ChevronDown,
  SortAsc,
  SortDesc,
} from 'lucide-react';
import { cn, formatBytes, formatRelativeTime } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { ListSkeleton, GridSkeleton } from '@/components/async/loading-states';
import { AsyncBoundary } from '@/components/async/suspense-wrapper';
import { useWorkspaceStore } from '@/stores/workspace-store';
import type { Artifact, ArtifactLogicalType } from '@/types';

interface ArtifactBrowserPaneProps {
  paneId: string;
}

// Mock data
const MOCK_ARTIFACTS: Artifact[] = [
  {
    id: 'art-1',
    tenantId: 'tenant-1',
    contentHash: 'sha256:abc123',
    logicalType: 'document',
    mimeType: 'application/pdf',
    sizeBytes: 2450000,
    filename: 'compliance-report-2024.pdf',
    createdByRunId: 'run-1',
    metadata: { pages: 45, author: 'John Smith' },
    storageKey: 'artifacts/art-1',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 'art-2',
    tenantId: 'tenant-1',
    contentHash: 'sha256:def456',
    logicalType: 'table',
    mimeType: 'application/x-parquet',
    sizeBytes: 1200000,
    filename: 'extracted-requirements.parquet',
    createdByRunId: 'run-1',
    metadata: { rows: 156, columns: 12 },
    storageKey: 'artifacts/art-2',
    createdAt: new Date(Date.now() - 43200000).toISOString(),
    updatedAt: new Date(Date.now() - 43200000).toISOString(),
  },
  {
    id: 'art-3',
    tenantId: 'tenant-1',
    contentHash: 'sha256:ghi789',
    logicalType: 'claim_set',
    mimeType: 'application/json',
    sizeBytes: 45000,
    filename: 'gdpr-claims.json',
    createdByRunId: 'run-1',
    metadata: { claimCount: 23 },
    storageKey: 'artifacts/art-3',
    createdAt: new Date(Date.now() - 21600000).toISOString(),
    updatedAt: new Date(Date.now() - 21600000).toISOString(),
  },
  {
    id: 'art-4',
    tenantId: 'tenant-1',
    contentHash: 'sha256:jkl012',
    logicalType: 'graph',
    mimeType: 'application/json',
    sizeBytes: 89000,
    filename: 'evidence-graph.json',
    createdByRunId: 'run-2',
    metadata: { nodes: 45, edges: 78 },
    storageKey: 'artifacts/art-4',
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    updatedAt: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: 'art-5',
    tenantId: 'tenant-1',
    contentHash: 'sha256:mno345',
    logicalType: 'image',
    mimeType: 'image/png',
    sizeBytes: 340000,
    filename: 'workflow-diagram.png',
    metadata: { width: 1920, height: 1080 },
    storageKey: 'artifacts/art-5',
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date(Date.now() - 3600000).toISOString(),
  },
];

const TYPE_ICONS: Record<ArtifactLogicalType, React.ElementType> = {
  document: FileText,
  table: Table,
  graph: FileJson,
  model: FileJson,
  image: Image,
  report: FileText,
  evidence: FileText,
  claim_set: FileJson,
  index_snapshot: File,
  plan: FileText,
  config: FileJson,
  other: File,
};

const TYPE_COLORS: Record<ArtifactLogicalType, string> = {
  document: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  table: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  graph: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  model: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  image: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
  report: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
  evidence: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  claim_set: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  index_snapshot: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  plan: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
  config: 'bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-400',
  other: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
};

type ViewMode = 'list' | 'grid';
type SortField = 'name' | 'date' | 'size' | 'type';
type SortDirection = 'asc' | 'desc';

export function ArtifactBrowserPane({ paneId }: ArtifactBrowserPaneProps) {
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [typeFilter, setTypeFilter] = useState<ArtifactLogicalType | 'all'>('all');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const { pinItem, pinnedItems, addPane } = useWorkspaceStore();

  const filteredArtifacts = useMemo(() => {
    let result = MOCK_ARTIFACTS;

    // Search filter
    if (search) {
      const lower = search.toLowerCase();
      result = result.filter(
        (art) =>
          art.filename?.toLowerCase().includes(lower) ||
          art.id.toLowerCase().includes(lower) ||
          art.logicalType.toLowerCase().includes(lower)
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      result = result.filter((art) => art.logicalType === typeFilter);
    }

    // Sort
    result = [...result].sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case 'name':
          cmp = (a.filename || a.id).localeCompare(b.filename || b.id);
          break;
        case 'date':
          cmp = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case 'size':
          cmp = a.sizeBytes - b.sizeBytes;
          break;
        case 'type':
          cmp = a.logicalType.localeCompare(b.logicalType);
          break;
      }
      return sortDirection === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [search, typeFilter, sortField, sortDirection]);

  const handleView = useCallback(
    (artifact: Artifact) => {
      addPane('main', {
        type: 'document-viewer',
        title: artifact.filename || artifact.id,
        resourceUri: `artifact://${artifact.id}`,
        closable: true,
        metadata: { artifactId: artifact.id },
      });
    },
    [addPane]
  );

  const handlePin = useCallback(
    (artifact: Artifact) => {
      pinItem({
        type: 'artifact',
        id: artifact.id,
        label: artifact.filename || artifact.id,
      });
    },
    [pinItem]
  );

  const isPinned = useCallback(
    (artifactId: string) => pinnedItems.some((p) => p.id === artifactId),
    [pinnedItems]
  );

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="p-3 border-b space-y-3">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search artifacts..."
              className="pl-8 h-9"
            />
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-1">
                <Filter className="h-3.5 w-3.5" />
                {typeFilter === 'all' ? 'All Types' : typeFilter}
                <ChevronDown className="h-3.5 w-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setTypeFilter('all')}>
                All Types
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {Object.keys(TYPE_ICONS).map((type) => (
                <DropdownMenuItem
                  key={type}
                  onClick={() => setTypeFilter(type as ArtifactLogicalType)}
                >
                  {type}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          <div className="flex items-center border rounded-md">
            <Button
              variant={viewMode === 'list' ? 'secondary' : 'ghost'}
              size="icon-sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="icon-sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Sort options */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Sort by:</span>
          {(['name', 'date', 'size', 'type'] as SortField[]).map((field) => (
            <button
              key={field}
              onClick={() => toggleSort(field)}
              className={cn(
                'flex items-center gap-0.5 px-1.5 py-0.5 rounded hover:bg-muted',
                sortField === field && 'font-medium text-foreground'
              )}
            >
              {field}
              {sortField === field &&
                (sortDirection === 'asc' ? (
                  <SortAsc className="h-3 w-3" />
                ) : (
                  <SortDesc className="h-3 w-3" />
                ))}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <AsyncBoundary
          loadingFallback={
            viewMode === 'list' ? <ListSkeleton count={8} /> : <GridSkeleton count={6} />
          }
        >
          {viewMode === 'list' ? (
            <div className="p-2 space-y-1">
              {filteredArtifacts.map((artifact) => (
                <ArtifactListItem
                  key={artifact.id}
                  artifact={artifact}
                  onView={handleView}
                  onPin={handlePin}
                  isPinned={isPinned(artifact.id)}
                />
              ))}
            </div>
          ) : (
            <div className="p-4 grid grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredArtifacts.map((artifact) => (
                <ArtifactGridItem
                  key={artifact.id}
                  artifact={artifact}
                  onView={handleView}
                  onPin={handlePin}
                  isPinned={isPinned(artifact.id)}
                />
              ))}
            </div>
          )}

          {filteredArtifacts.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              <File className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No artifacts found</p>
            </div>
          )}
        </AsyncBoundary>
      </ScrollArea>

      {/* Footer */}
      <div className="px-3 py-2 border-t text-xs text-muted-foreground">
        {filteredArtifacts.length} artifact{filteredArtifacts.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}

interface ArtifactItemProps {
  artifact: Artifact;
  onView: (artifact: Artifact) => void;
  onPin: (artifact: Artifact) => void;
  isPinned: boolean;
}

function ArtifactListItem({ artifact, onView, onPin, isPinned }: ArtifactItemProps) {
  const Icon = TYPE_ICONS[artifact.logicalType] || File;

  return (
    <div className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/50 group">
      <div className={cn('h-10 w-10 rounded flex items-center justify-center', TYPE_COLORS[artifact.logicalType])}>
        <Icon className="h-5 w-5" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{artifact.filename || artifact.id}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{formatBytes(artifact.sizeBytes)}</span>
          <span>{formatRelativeTime(artifact.createdAt)}</span>
        </div>
      </div>

      <Badge variant="outline" className="text-xs shrink-0">
        {artifact.logicalType}
      </Badge>

      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="icon-sm" onClick={() => onView(artifact)}>
          <Eye className="h-4 w-4" />
        </Button>
        <Button
          variant={isPinned ? 'secondary' : 'ghost'}
          size="icon-sm"
          onClick={() => onPin(artifact)}
        >
          <Pin className={cn('h-4 w-4', isPinned && 'fill-current')} />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon-sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Download className="h-4 w-4 mr-2" />
              Download
            </DropdownMenuItem>
            <DropdownMenuItem>Copy ID</DropdownMenuItem>
            <DropdownMenuItem>View in run</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}

function ArtifactGridItem({ artifact, onView, onPin, isPinned }: ArtifactItemProps) {
  const Icon = TYPE_ICONS[artifact.logicalType] || File;

  return (
    <div
      className="rounded-lg border bg-card p-3 hover:shadow-md transition-shadow cursor-pointer group"
      onClick={() => onView(artifact)}
    >
      <div className="flex items-start justify-between mb-2">
        <div className={cn('h-10 w-10 rounded flex items-center justify-center', TYPE_COLORS[artifact.logicalType])}>
          <Icon className="h-5 w-5" />
        </div>

        <Button
          variant={isPinned ? 'secondary' : 'ghost'}
          size="icon-xs"
          className="opacity-0 group-hover:opacity-100"
          onClick={(e) => {
            e.stopPropagation();
            onPin(artifact);
          }}
        >
          <Pin className={cn('h-3.5 w-3.5', isPinned && 'fill-current')} />
        </Button>
      </div>

      <p className="text-sm font-medium truncate">{artifact.filename || artifact.id}</p>
      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
        <span>{formatBytes(artifact.sizeBytes)}</span>
        <span>{artifact.logicalType}</span>
      </div>
    </div>
  );
}

// Add DropdownMenu components that we're using
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';

const DropdownMenu = DropdownMenuPrimitive.Root;
const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;

const DropdownMenuContent = ({
  className,
  sideOffset = 4,
  ...props
}: React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content> & {
  sideOffset?: number;
}) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      sideOffset={sideOffset}
      className={cn(
        'z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md',
        'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
        className
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
);

const DropdownMenuItem = ({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item>) => (
  <DropdownMenuPrimitive.Item
    className={cn(
      'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      className
    )}
    {...props}
  />
);

const DropdownMenuSeparator = ({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>) => (
  <DropdownMenuPrimitive.Separator
    className={cn('-mx-1 my-1 h-px bg-muted', className)}
    {...props}
  />
);
