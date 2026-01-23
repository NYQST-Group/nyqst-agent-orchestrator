/**
 * Explorer panel - hierarchical navigation
 *
 * Sections:
 * - Pointers (namespaces -> pointers)
 * - Recent Artifacts
 * - Recent Runs
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  GitBranch,
  FileBox,
  Play,
  RefreshCw,
} from 'lucide-react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { pointersApi, artifactsApi, runsApi } from '@/api/client'
import { useWorkbenchStore } from '@/stores/workbench-store'
import type { Pointer, Artifact, Run } from '@/types/api'

interface TreeItemProps {
  icon: React.ReactNode
  label: string
  isExpanded?: boolean
  isSelected?: boolean
  onClick?: () => void
  onToggle?: () => void
  children?: React.ReactNode
  depth?: number
}

function TreeItem({
  icon,
  label,
  isExpanded,
  isSelected,
  onClick,
  onToggle,
  children,
  depth = 0,
}: TreeItemProps) {
  const hasChildren = !!children

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-1 px-2 py-1 cursor-pointer hover:bg-accent rounded-sm',
          isSelected && 'bg-accent'
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
        onClick={onClick}
      >
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggle?.()
            }}
            className="p-0.5 hover:bg-muted rounded"
          >
            {isExpanded ? (
              <ChevronDown className="h-3 w-3" />
            ) : (
              <ChevronRight className="h-3 w-3" />
            )}
          </button>
        ) : (
          <span className="w-4" />
        )}
        <span className="text-muted-foreground">{icon}</span>
        <span className="text-sm truncate">{label}</span>
      </div>
      {isExpanded && children}
    </div>
  )
}

function PointersSection() {
  const [expanded, setExpanded] = useState(true)
  const [expandedNamespaces, setExpandedNamespaces] = useState<Set<string>>(
    new Set()
  )
  const { selectedPointerId, selectPointer, openTab } = useWorkbenchStore()

  const { data: pointers, isLoading, refetch } = useQuery({
    queryKey: ['pointers'],
    queryFn: () => pointersApi.list(),
  })

  // Group pointers by namespace
  const namespaces = pointers?.reduce(
    (acc, pointer) => {
      if (!acc[pointer.namespace]) {
        acc[pointer.namespace] = []
      }
      acc[pointer.namespace].push(pointer)
      return acc
    },
    {} as Record<string, Pointer[]>
  )

  const toggleNamespace = (ns: string) => {
    setExpandedNamespaces((prev) => {
      const next = new Set(prev)
      if (next.has(ns)) {
        next.delete(ns)
      } else {
        next.add(ns)
      }
      return next
    })
  }

  const handlePointerClick = (pointer: Pointer) => {
    selectPointer(pointer.id)
    openTab({
      type: 'pointer',
      title: `${pointer.namespace}/${pointer.name}`,
      resourceId: pointer.id,
    })
  }

  return (
    <div>
      <div className="flex items-center justify-between px-2 py-1">
        <button
          className="flex items-center gap-1 text-xs font-semibold uppercase text-muted-foreground hover:text-foreground"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
          Pointers
        </button>
        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
        </Button>
      </div>

      {expanded && namespaces && (
        <div className="space-y-0.5">
          {Object.entries(namespaces).map(([namespace, nsPointers]) => (
            <TreeItem
              key={namespace}
              icon={
                expandedNamespaces.has(namespace) ? (
                  <FolderOpen className="h-4 w-4" />
                ) : (
                  <Folder className="h-4 w-4" />
                )
              }
              label={namespace}
              isExpanded={expandedNamespaces.has(namespace)}
              onToggle={() => toggleNamespace(namespace)}
              depth={0}
            >
              {nsPointers.map((pointer) => (
                <TreeItem
                  key={pointer.id}
                  icon={<GitBranch className="h-4 w-4" />}
                  label={pointer.name}
                  isSelected={selectedPointerId === pointer.id}
                  onClick={() => handlePointerClick(pointer)}
                  depth={1}
                />
              ))}
            </TreeItem>
          ))}
        </div>
      )}
    </div>
  )
}

function ArtifactsSection() {
  const [expanded, setExpanded] = useState(false)
  const { openTab } = useWorkbenchStore()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['artifacts', 'recent'],
    queryFn: () => artifactsApi.list(1, 10),
    enabled: expanded,
  })

  const handleArtifactClick = (artifact: Artifact) => {
    openTab({
      type: 'artifact',
      title: artifact.original_filename || artifact.sha256.slice(0, 12),
      resourceId: artifact.sha256,
    })
  }

  return (
    <div>
      <div className="flex items-center justify-between px-2 py-1">
        <button
          className="flex items-center gap-1 text-xs font-semibold uppercase text-muted-foreground hover:text-foreground"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
          Recent Artifacts
        </button>
        {expanded && (
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
          </Button>
        )}
      </div>

      {expanded && data?.items && (
        <div className="space-y-0.5">
          {data.items.map((artifact) => (
            <TreeItem
              key={artifact.sha256}
              icon={<FileBox className="h-4 w-4" />}
              label={artifact.original_filename || artifact.sha256.slice(0, 16)}
              onClick={() => handleArtifactClick(artifact)}
              depth={0}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function RunsSection() {
  const [expanded, setExpanded] = useState(true)
  const { selectedRunId, selectRun } = useWorkbenchStore()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['runs', 'recent'],
    queryFn: () => runsApi.list(undefined, undefined, 1, 10),
  })

  const getStatusColor = (status: Run['status']) => {
    switch (status) {
      case 'running':
        return 'text-blue-500'
      case 'completed':
        return 'text-green-500'
      case 'failed':
        return 'text-red-500'
      default:
        return 'text-muted-foreground'
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between px-2 py-1">
        <button
          className="flex items-center gap-1 text-xs font-semibold uppercase text-muted-foreground hover:text-foreground"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
          Recent Runs
        </button>
        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
        </Button>
      </div>

      {expanded && data?.items && (
        <div className="space-y-0.5">
          {data.items.map((run) => (
            <TreeItem
              key={run.id}
              icon={<Play className={cn('h-4 w-4', getStatusColor(run.status))} />}
              label={`${run.run_type} - ${run.id.slice(0, 8)}`}
              isSelected={selectedRunId === run.id}
              onClick={() => selectRun(run.id)}
              depth={0}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function ExplorerPanel() {
  return (
    <div className="flex h-full flex-col border-r bg-background">
      <div className="px-3 py-2">
        <h2 className="text-sm font-semibold">Explorer</h2>
      </div>
      <Separator />
      <ScrollArea className="flex-1">
        <div className="space-y-2 p-2">
          <PointersSection />
          <Separator />
          <RunsSection />
          <Separator />
          <ArtifactsSection />
        </div>
      </ScrollArea>
    </div>
  )
}
