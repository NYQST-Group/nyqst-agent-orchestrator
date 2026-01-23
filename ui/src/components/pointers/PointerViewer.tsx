/**
 * Pointer viewer component with history and manifest resolution
 */

import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { GitBranch, History, ArrowRight, FileStack } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { pointersApi } from '@/api/client'
import { truncateHash } from '@/lib/utils'
import { useWorkbenchStore } from '@/stores/workbench-store'

interface PointerViewerProps {
  pointerId: string
}

export function PointerViewer({ pointerId }: PointerViewerProps) {
  const { openTab } = useWorkbenchStore()

  const { data: pointers } = useQuery({
    queryKey: ['pointers'],
    queryFn: () => pointersApi.list(),
  })

  const pointer = pointers?.find((p) => p.id === pointerId)

  const { data: history } = useQuery({
    queryKey: ['pointer-history', pointerId],
    queryFn: () => pointersApi.getHistory(pointerId),
    enabled: !!pointer,
  })

  const { data: manifest } = useQuery({
    queryKey: ['pointer-resolve', pointer?.namespace, pointer?.name],
    queryFn: () => pointersApi.resolve(pointer!.namespace, pointer!.name),
    enabled: !!pointer?.head_sha256,
  })

  if (!pointer) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground">Loading pointer...</div>
      </div>
    )
  }

  const handleManifestClick = (sha256: string) => {
    openTab({
      type: 'manifest',
      title: `Manifest ${truncateHash(sha256)}`,
      resourceId: sha256,
    })
  }

  return (
    <div className="h-full p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-start gap-4 mb-6">
          <GitBranch className="h-10 w-10 text-muted-foreground mt-1" />
          <div className="flex-1">
            <h1 className="text-xl font-semibold">
              {pointer.namespace}/{pointer.name}
            </h1>
            <p className="text-sm text-muted-foreground font-mono mt-1">
              {pointer.id}
            </p>
          </div>
          <div className="text-right">
            <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
              v{pointer.version}
            </span>
          </div>
        </div>

        <Separator className="my-4" />

        {/* Current HEAD */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <FileStack className="h-4 w-4" />
            Current HEAD
          </h2>
          {pointer.head_sha256 ? (
            <div className="rounded-lg border p-4 bg-card">
              <button
                className="text-sm font-mono text-blue-600 hover:underline"
                onClick={() => handleManifestClick(pointer.head_sha256!)}
              >
                {pointer.head_sha256}
              </button>
              {manifest && (
                <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Entries:</span>{' '}
                    {manifest.entry_count}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Created:</span>{' '}
                    {format(new Date(manifest.created_at), 'PP')}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="rounded-lg border p-4 bg-muted/50 text-center text-muted-foreground">
              No manifest attached
            </div>
          )}
        </div>

        <Separator className="my-4" />

        {/* Tabs */}
        <Tabs defaultValue="history">
          <TabsList>
            <TabsTrigger value="history">
              <History className="h-4 w-4 mr-2" />
              History ({history?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="info">Info</TabsTrigger>
          </TabsList>

          <TabsContent value="history" className="mt-4">
            <ScrollArea className="h-[300px]">
              {!history || history.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No history records
                </div>
              ) : (
                <div className="space-y-3">
                  {history.map((entry, index) => (
                    <div
                      key={entry.id}
                      className="rounded-lg border p-3 bg-card"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">
                          Version {entry.version}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {format(new Date(entry.changed_at), 'PPpp')}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm font-mono">
                        <span className="text-muted-foreground">
                          {entry.from_sha256
                            ? truncateHash(entry.from_sha256)
                            : 'null'}
                        </span>
                        <ArrowRight className="h-4 w-4 text-muted-foreground" />
                        <button
                          className="text-blue-600 hover:underline"
                          onClick={() => handleManifestClick(entry.to_sha256)}
                        >
                          {truncateHash(entry.to_sha256)}
                        </button>
                      </div>
                      {entry.reason && (
                        <p className="mt-2 text-sm text-muted-foreground">
                          {entry.reason}
                        </p>
                      )}
                      {entry.changed_by && (
                        <p className="mt-1 text-xs text-muted-foreground">
                          by {entry.changed_by}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="info" className="mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Namespace</p>
                <p className="text-sm font-medium">{pointer.namespace}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="text-sm font-medium">{pointer.name}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Created</p>
                <p className="text-sm font-medium">
                  {format(new Date(pointer.created_at), 'PPpp')}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Updated</p>
                <p className="text-sm font-medium">
                  {format(new Date(pointer.updated_at), 'PPpp')}
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
