/**
 * Details/properties panel - shows context-sensitive information
 */

import { useQuery } from '@tanstack/react-query'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { useWorkbenchStore } from '@/stores/workbench-store'
import { pointersApi, runsApi, artifactsApi } from '@/api/client'
import { formatBytes, truncateHash } from '@/lib/utils'
import { format } from 'date-fns'

interface PropertyRowProps {
  label: string
  value: React.ReactNode
  mono?: boolean
}

function PropertyRow({ label, value, mono }: PropertyRowProps) {
  return (
    <div className="flex justify-between py-1">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className={`text-sm ${mono ? 'font-mono' : ''}`}>{value}</span>
    </div>
  )
}

function PointerDetails({ pointerId }: { pointerId: string }) {
  const { data: pointers } = useQuery({
    queryKey: ['pointers'],
    queryFn: () => pointersApi.list(),
  })

  const pointer = pointers?.find((p) => p.id === pointerId)

  if (!pointer) {
    return <div className="p-4 text-sm text-muted-foreground">Loading...</div>
  }

  return (
    <div className="space-y-4 p-4">
      <div>
        <h3 className="text-sm font-semibold mb-2">Pointer</h3>
        <div className="space-y-1">
          <PropertyRow label="Namespace" value={pointer.namespace} />
          <PropertyRow label="Name" value={pointer.name} />
          <PropertyRow label="Version" value={pointer.version} />
          <PropertyRow
            label="HEAD"
            value={pointer.head_sha256 ? truncateHash(pointer.head_sha256) : 'null'}
            mono
          />
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2">Timestamps</h3>
        <div className="space-y-1">
          <PropertyRow
            label="Created"
            value={format(new Date(pointer.created_at), 'PPpp')}
          />
          <PropertyRow
            label="Updated"
            value={format(new Date(pointer.updated_at), 'PPpp')}
          />
        </div>
      </div>
    </div>
  )
}

function RunDetails({ runId }: { runId: string }) {
  const { data: run } = useQuery({
    queryKey: ['run', runId],
    queryFn: () => runsApi.get(runId),
  })

  if (!run) {
    return <div className="p-4 text-sm text-muted-foreground">Loading...</div>
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    }
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs ${colors[status] || ''}`}>
        {status}
      </span>
    )
  }

  return (
    <div className="space-y-4 p-4">
      <div>
        <h3 className="text-sm font-semibold mb-2">Run</h3>
        <div className="space-y-1">
          <PropertyRow label="ID" value={truncateHash(run.id)} mono />
          <PropertyRow label="Type" value={run.run_type} />
          <PropertyRow label="Status" value={getStatusBadge(run.status)} />
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2">Manifests</h3>
        <div className="space-y-1">
          <PropertyRow
            label="Input"
            value={
              run.input_manifest_sha256
                ? truncateHash(run.input_manifest_sha256)
                : '-'
            }
            mono
          />
          <PropertyRow
            label="Output"
            value={
              run.output_manifest_sha256
                ? truncateHash(run.output_manifest_sha256)
                : '-'
            }
            mono
          />
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2">Timestamps</h3>
        <div className="space-y-1">
          <PropertyRow
            label="Created"
            value={format(new Date(run.created_at), 'PPpp')}
          />
          {run.started_at && (
            <PropertyRow
              label="Started"
              value={format(new Date(run.started_at), 'PPpp')}
            />
          )}
          {run.completed_at && (
            <PropertyRow
              label="Completed"
              value={format(new Date(run.completed_at), 'PPpp')}
            />
          )}
        </div>
      </div>

      {run.error_message && (
        <>
          <Separator />
          <div>
            <h3 className="text-sm font-semibold mb-2 text-red-600">Error</h3>
            <p className="text-sm text-red-600 bg-red-50 p-2 rounded">
              {run.error_message}
            </p>
          </div>
        </>
      )}
    </div>
  )
}

function ArtifactDetails({ sha256 }: { sha256: string }) {
  const { data: artifact } = useQuery({
    queryKey: ['artifact', sha256],
    queryFn: () => artifactsApi.get(sha256),
  })

  if (!artifact) {
    return <div className="p-4 text-sm text-muted-foreground">Loading...</div>
  }

  return (
    <div className="space-y-4 p-4">
      <div>
        <h3 className="text-sm font-semibold mb-2">Artifact</h3>
        <div className="space-y-1">
          <PropertyRow label="SHA-256" value={truncateHash(artifact.sha256)} mono />
          <PropertyRow label="Media Type" value={artifact.media_type} />
          <PropertyRow label="Size" value={formatBytes(artifact.size_bytes)} />
          {artifact.original_filename && (
            <PropertyRow label="Filename" value={artifact.original_filename} />
          )}
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2">References</h3>
        <div className="space-y-1">
          <PropertyRow label="Ref Count" value={artifact.reference_count} />
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2">Timestamps</h3>
        <div className="space-y-1">
          <PropertyRow
            label="Created"
            value={format(new Date(artifact.created_at), 'PPpp')}
          />
        </div>
      </div>
    </div>
  )
}

export function DetailsPanel() {
  const { tabs, activeTabId } = useWorkbenchStore()
  const activeTab = tabs.find((t) => t.id === activeTabId)

  return (
    <div className="flex h-full flex-col border-l bg-background">
      <div className="px-3 py-2 border-b">
        <h2 className="text-sm font-semibold">Details</h2>
      </div>
      <ScrollArea className="flex-1">
        {!activeTab ? (
          <div className="p-4 text-sm text-muted-foreground">
            Select an item to view details
          </div>
        ) : activeTab.type === 'pointer' ? (
          <PointerDetails pointerId={activeTab.resourceId} />
        ) : activeTab.type === 'run' ? (
          <RunDetails runId={activeTab.resourceId} />
        ) : activeTab.type === 'artifact' ? (
          <ArtifactDetails sha256={activeTab.resourceId} />
        ) : (
          <div className="p-4 text-sm text-muted-foreground">
            No details available
          </div>
        )}
      </ScrollArea>
    </div>
  )
}
