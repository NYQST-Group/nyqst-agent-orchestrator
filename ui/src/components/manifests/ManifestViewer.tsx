/**
 * Manifest viewer component showing entries and history
 */

import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import {
  FileStack,
  FileBox,
  Folder,
  ChevronRight,
  GitCommit,
} from 'lucide-react'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { manifestsApi } from '@/api/client'
import { formatBytes, truncateHash } from '@/lib/utils'
import { useWorkbenchStore } from '@/stores/workbench-store'
import type { ManifestEntry } from '@/types/api'

interface ManifestViewerProps {
  sha256: string
}

function EntryRow({ entry, onClick }: { entry: ManifestEntry; onClick: () => void }) {
  const isManifest = entry.ref_type === 'manifest'

  return (
    <button
      className="w-full flex items-center gap-3 px-3 py-2 hover:bg-muted rounded-md text-left"
      onClick={onClick}
    >
      {isManifest ? (
        <Folder className="h-4 w-4 text-blue-500" />
      ) : (
        <FileBox className="h-4 w-4 text-gray-500" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{entry.path}</p>
        <p className="text-xs text-muted-foreground font-mono">
          {truncateHash(entry.ref_sha256)}
        </p>
      </div>
      <div className="text-right">
        {entry.size_bytes !== undefined && (
          <p className="text-xs text-muted-foreground">
            {formatBytes(entry.size_bytes)}
          </p>
        )}
        {entry.media_type && (
          <p className="text-xs text-muted-foreground">{entry.media_type}</p>
        )}
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground" />
    </button>
  )
}

export function ManifestViewer({ sha256 }: ManifestViewerProps) {
  const { openTab } = useWorkbenchStore()

  const { data: manifest, isLoading } = useQuery({
    queryKey: ['manifest', sha256],
    queryFn: () => manifestsApi.get(sha256),
  })

  const { data: entries } = useQuery({
    queryKey: ['manifest-entries', sha256],
    queryFn: () => manifestsApi.getEntries(sha256),
    enabled: !!manifest,
  })

  const { data: history } = useQuery({
    queryKey: ['manifest-history', sha256],
    queryFn: () => manifestsApi.getHistory(sha256),
    enabled: !!manifest,
  })

  if (isLoading || !manifest) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground">Loading manifest...</div>
      </div>
    )
  }

  const handleEntryClick = (entry: ManifestEntry) => {
    if (entry.ref_type === 'manifest') {
      openTab({
        type: 'manifest',
        title: `Manifest ${truncateHash(entry.ref_sha256)}`,
        resourceId: entry.ref_sha256,
      })
    } else {
      openTab({
        type: 'artifact',
        title: entry.path.split('/').pop() || truncateHash(entry.ref_sha256),
        resourceId: entry.ref_sha256,
      })
    }
  }

  const handleManifestClick = (manifestSha: string) => {
    openTab({
      type: 'manifest',
      title: `Manifest ${truncateHash(manifestSha)}`,
      resourceId: manifestSha,
    })
  }

  return (
    <div className="h-full p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-start gap-4 mb-6">
          <FileStack className="h-10 w-10 text-muted-foreground mt-1" />
          <div className="flex-1">
            <h1 className="text-xl font-semibold">Manifest</h1>
            <p className="text-sm text-muted-foreground font-mono mt-1">
              {sha256}
            </p>
          </div>
        </div>

        <Separator className="my-4" />

        {/* Metadata */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Entries</p>
            <p className="text-sm font-medium">{manifest.entry_count}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Total Size</p>
            <p className="text-sm font-medium">
              {formatBytes(manifest.total_size_bytes)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Parent</p>
            <p className="text-sm font-mono">
              {manifest.parent_sha256 ? (
                <button
                  className="text-blue-600 hover:underline"
                  onClick={() => handleManifestClick(manifest.parent_sha256!)}
                >
                  {truncateHash(manifest.parent_sha256)}
                </button>
              ) : (
                <span className="text-muted-foreground">None</span>
              )}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="text-sm font-medium">
              {format(new Date(manifest.created_at), 'PPpp')}
            </p>
          </div>
        </div>

        {manifest.message && (
          <div className="mb-6 p-3 bg-muted rounded-lg">
            <p className="text-sm">{manifest.message}</p>
            {manifest.created_by && (
              <p className="text-xs text-muted-foreground mt-1">
                by {manifest.created_by}
              </p>
            )}
          </div>
        )}

        <Separator className="my-4" />

        {/* Tabs */}
        <Tabs defaultValue="entries">
          <TabsList>
            <TabsTrigger value="entries">
              Entries ({entries?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="history">
              History ({history?.length || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="entries" className="mt-4">
            <ScrollArea className="h-[400px]">
              {!entries || entries.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No entries
                </div>
              ) : (
                <div className="space-y-1">
                  {entries.map((entry) => (
                    <EntryRow
                      key={entry.path}
                      entry={entry}
                      onClick={() => handleEntryClick(entry)}
                    />
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="history" className="mt-4">
            <ScrollArea className="h-[400px]">
              {!history || history.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No history (root manifest)
                </div>
              ) : (
                <div className="space-y-2">
                  {history.map((m, index) => (
                    <button
                      key={m.sha256}
                      className="w-full flex items-center gap-3 p-3 rounded-lg border hover:bg-muted text-left"
                      onClick={() => handleManifestClick(m.sha256)}
                    >
                      <GitCommit className="h-5 w-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm font-mono">
                          {truncateHash(m.sha256)}
                        </p>
                        {m.message && (
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {m.message}
                          </p>
                        )}
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <p>{m.entry_count} entries</p>
                        <p>{format(new Date(m.created_at), 'PP')}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
