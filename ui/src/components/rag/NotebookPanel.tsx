import { useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BookOpen, FileUp, Sparkles } from 'lucide-react'
import { artifactsApi, manifestsApi, pointersApi, ragApi } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/use-toast'
import { truncateHash } from '@/lib/utils'
import { useWorkbenchStore } from '@/stores/workbench-store'
import type { ManifestEntry, Pointer, RagAskResponse } from '@/types/api'

function makeUniquePath(existingPaths: Set<string>, desiredPath: string) {
  if (!existingPaths.has(desiredPath)) return desiredPath

  const dotIndex = desiredPath.lastIndexOf('.')
  const base = dotIndex > 0 ? desiredPath.slice(0, dotIndex) : desiredPath
  const ext = dotIndex > 0 ? desiredPath.slice(dotIndex) : ''

  let i = 2
   
  while (true) {
    const candidate = `${base} (${i})${ext}`
    if (!existingPaths.has(candidate)) return candidate
    i += 1
  }
}

export function NotebookPanel({ pointer }: { pointer: Pointer }) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const { openTab } = useWorkbenchStore()

  const fileInputRef = useRef<HTMLInputElement>(null)

  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(8)
  const [lastAnswer, setLastAnswer] = useState<RagAskResponse | null>(null)

  const manifestSha = pointer.manifest_sha256 ?? null

  const entriesQuery = useQuery({
    queryKey: ['manifest-entries', manifestSha],
    queryFn: () => manifestsApi.getEntries(manifestSha!),
    enabled: !!manifestSha,
  })

  const entries = entriesQuery.data ?? []

  const existingPaths = useMemo(() => new Set(entries.map((e) => e.path)), [entries])

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      const baseEntries: ManifestEntry[] = entries
      const usedPaths = new Set(existingPaths)
      const newEntries = [...baseEntries]

      for (const file of files) {
        const upload = await artifactsApi.upload(file)
        const path = makeUniquePath(usedPaths, file.name)
        usedPaths.add(path)
        newEntries.push({
          path,
          artifact_sha256: upload.sha256,
          metadata: {
            filename: file.name,
            media_type: file.type || undefined,
            size_bytes: file.size,
          },
        })
      }

      const created = await manifestsApi.create({
        entries: newEntries,
        parent_sha256: manifestSha,
        message: `Added ${files.length} file${files.length === 1 ? '' : 's'}`,
        metadata: { source: 'ui' },
      })

      const advance = await pointersApi.advance(pointer.id, {
        manifest_sha256: created.sha256,
        expected_sha256: manifestSha,
        reason: 'upload',
      })

      if (!advance.success) {
        throw new Error('Pointer advance conflict. Refresh and retry.')
      }

      return { manifest_sha256: created.sha256 }
    },
    onSuccess: async (result) => {
      toast({
        title: 'Uploaded',
        description: `Notebook updated: ${truncateHash(result.manifest_sha256)}`,
      })
      await queryClient.invalidateQueries({ queryKey: ['pointers'] })
      await queryClient.invalidateQueries({ queryKey: ['pointer-history', pointer.id] })
      await queryClient.invalidateQueries({ queryKey: ['manifest-entries', result.manifest_sha256] })
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'Unknown error',
      })
    },
  })

  const askMutation = useMutation({
    mutationFn: async () => {
      if (!pointer.manifest_sha256) {
        throw new Error('Upload files first (notebook is empty).')
      }
      if (!question.trim()) {
        throw new Error('Enter a question.')
      }
      return ragApi.ask({ pointer_id: pointer.id, question, top_k: topK })
    },
    onSuccess: (result) => {
      setLastAnswer(result)
      openTab({
        type: 'run',
        title: `RAG Ask ${result.run_id.slice(0, 8)}`,
        resourceId: result.run_id,
      })
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: 'Ask failed',
        description: error instanceof Error ? error.message : 'Unknown error',
      })
    },
  })

  const handlePickFiles = () => fileInputRef.current?.click()

  const handleFilesSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    if (files.length === 0) return
    uploadMutation.mutate(files)
    e.target.value = ''
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Notebook
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Upload documents, then ask questions with citations. Indexing runs automatically as sources change.
          </p>
        </div>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFilesSelected}
          />
          <Button
            size="sm"
            onClick={handlePickFiles}
            disabled={uploadMutation.isPending || askMutation.isPending}
          >
            <FileUp className="h-4 w-4 mr-2" />
            Upload
          </Button>
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2">Files</h3>
        {entriesQuery.isLoading ? (
          <div className="text-sm text-muted-foreground">Loading…</div>
        ) : entries.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            No files yet. Upload PDFs or DOCX to get started.
          </div>
        ) : (
          <div className="space-y-1">
            {entries.map((e) => (
              <div
                key={`${e.path}-${e.artifact_sha256}`}
                className="flex items-center justify-between gap-3 rounded-md border px-3 py-2"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{e.path}</p>
                  <p className="text-xs text-muted-foreground font-mono">
                    {truncateHash(e.artifact_sha256, 16)}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    openTab({
                      type: 'artifact',
                      title: e.path.split('/').pop() || truncateHash(e.artifact_sha256, 12),
                      resourceId: e.artifact_sha256,
                    })
                  }
                >
                  Open
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      <Separator />

      <div>
        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <Sparkles className="h-4 w-4" />
          Ask
        </h3>

        <div className="space-y-2">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Ask a question about the notebook…"
          />

          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Top-K</span>
              <input
                type="number"
                min={1}
                max={50}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-20 rounded-md border px-2 py-1 text-sm"
              />
            </div>
            <Button
              onClick={() => askMutation.mutate()}
              disabled={askMutation.isPending || uploadMutation.isPending}
            >
              {askMutation.isPending ? 'Asking…' : 'Ask'}
            </Button>
          </div>
        </div>

        {lastAnswer && (
          <div className="mt-4 space-y-3">
            <div className="rounded-lg border p-4 bg-card">
              <p className="text-sm whitespace-pre-wrap">{lastAnswer.answer}</p>
            </div>

            {lastAnswer.sources.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                  Sources
                </h4>
                <div className="space-y-2">
                  {lastAnswer.sources.map((s, i) => (
                    <div
                      key={s.chunk_id}
                      className="rounded-md border p-3 bg-muted/30"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">
                            [{i + 1}] {s.path || truncateHash(s.artifact_sha256, 16)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            score {s.score.toFixed(3)}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            openTab({
                              type: 'artifact',
                              title:
                                s.path?.split('/').pop() ||
                                truncateHash(s.artifact_sha256, 12),
                              resourceId: s.artifact_sha256,
                            })
                          }
                        >
                          Open
                        </Button>
                      </div>
                      <p className="mt-2 text-xs text-muted-foreground whitespace-pre-wrap">
                        {s.content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
