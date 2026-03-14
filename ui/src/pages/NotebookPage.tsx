import { useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { BookOpen, ChevronLeft, FileUp, Search } from 'lucide-react'

import type { ManifestEntry, Pointer, RagAskResponse } from '@/types/api'
import { artifactsApi, manifestsApi, pointersApi, ragApi } from '@/api/client'
import { ArtifactViewer } from '@/components/artifacts/ArtifactViewer'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/use-toast'
import { truncateHash } from '@/lib/utils'

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

export function NotebookPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const fileInputRef = useRef<HTMLInputElement>(null)

  const [selectedArtifactSha, setSelectedArtifactSha] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(8)
  const [lastAnswer, setLastAnswer] = useState<RagAskResponse | null>(null)
  const [search, setSearch] = useState('')

  const pointersQuery = useQuery({
    queryKey: ['pointers'],
    queryFn: () => pointersApi.list(),
  })

  const pointer: Pointer | undefined = useMemo(() => {
    if (!id) return undefined
    return (pointersQuery.data ?? []).find((p) => p.id === id)
  }, [id, pointersQuery.data])

  const manifestSha = pointer?.manifest_sha256 ?? null

  const entriesQuery = useQuery({
    queryKey: ['manifest-entries', manifestSha],
    queryFn: () => manifestsApi.getEntries(manifestSha!),
    enabled: !!manifestSha,
  })

  const entries = entriesQuery.data ?? []
  const existingPaths = useMemo(() => new Set(entries.map((e) => e.path)), [entries])

  const filteredEntries = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return entries
    return entries.filter((e) => e.path.toLowerCase().includes(term))
  }, [entries, search])

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      if (!pointer) throw new Error('Notebook not found.')

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

      if (!advance.success) throw new Error('Notebook update conflict. Refresh and retry.')

      return created.sha256
    },
    onSuccess: async (newSha) => {
      toast({ title: 'Uploaded', description: `Notebook updated: ${truncateHash(newSha)}` })
      await queryClient.invalidateQueries({ queryKey: ['pointers'] })
      await queryClient.invalidateQueries({ queryKey: ['manifest-entries', newSha] })
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
      if (!pointer) throw new Error('Notebook not found.')
      if (!pointer.manifest_sha256) throw new Error('Upload sources first (notebook is empty).')
      if (!question.trim()) throw new Error('Enter a question.')
      return ragApi.ask({ pointer_id: pointer.id, question, top_k: topK })
    },
    onSuccess: (result) => {
      setLastAnswer(result)
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

  if (!id) {
    return null
  }

  if (pointersQuery.isLoading) {
    return <div className="p-6 text-sm text-muted-foreground">Loading…</div>
  }

  if (!pointer) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">Notebook not found.</p>
        <div className="mt-4">
          <Button onClick={() => navigate('/docs')}>
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to notebooks
          </Button>
        </div>
      </div>
    )
  }

  const busy = uploadMutation.isPending || askMutation.isPending

  return (
    <div className="mx-auto flex h-full max-w-7xl flex-col px-6 py-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => navigate('/docs')}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              Source Library
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                <h1 className="truncate text-base font-semibold">{pointer.name}</h1>
              </div>
              <p className="mt-0.5 text-xs text-muted-foreground">
                {pointer.manifest_sha256 ? 'Sources ready' : 'No sources yet'} · {entries.length} file
                {entries.length === 1 ? '' : 's'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFilesSelected}
            />
            <Button size="sm" onClick={handlePickFiles} disabled={busy}>
              <FileUp className="mr-2 h-4 w-4" />
              Upload
            </Button>
          </div>
      </header>

      <div className="mt-4 grid min-h-[640px] flex-1 grid-cols-12 gap-4">
        {/* Sources */}
        <div className="col-span-3 flex h-full flex-col rounded-lg border bg-card">
          <div className="px-4 py-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Sources</h2>
              <span className="text-xs text-muted-foreground">{entries.length}</span>
            </div>
            <div className="mt-2 flex items-center gap-2 rounded-md border bg-background px-2 py-1">
              <Search className="h-4 w-4 text-muted-foreground" />
              <input
                className="w-full bg-transparent text-sm outline-none"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search sources…"
              />
            </div>
          </div>
          <Separator />
          <div className="flex-1 overflow-auto">
            {entriesQuery.isLoading ? (
              <div className="px-4 py-6 text-sm text-muted-foreground">Loading…</div>
            ) : entries.length === 0 ? (
              <div className="px-4 py-6 text-sm text-muted-foreground">
                Upload PDFs, DOCX, HTML, or text files to start building this source library.
              </div>
            ) : (
              <div className="divide-y">
                {filteredEntries.map((e) => (
                  <button
                    key={`${e.path}-${e.artifact_sha256}`}
                    className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-accent"
                    onClick={() => setSelectedArtifactSha(e.artifact_sha256)}
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{e.path}</p>
                      <p className="mt-0.5 font-mono text-[11px] text-muted-foreground">
                        {truncateHash(e.artifact_sha256, 16)}
                      </p>
                    </div>
                    <div className="text-xs text-muted-foreground">View</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat */}
        <div className="col-span-6 flex h-full flex-col rounded-lg border bg-card">
          <div className="px-4 py-3">
            <h2 className="text-sm font-semibold">Ask</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Ask questions grounded in your sources. Indexing runs automatically as sources change.
            </p>
          </div>
          <Separator />
          <div className="flex-1 overflow-auto px-4 py-4">
            {!lastAnswer ? (
              <div className="text-sm text-muted-foreground">
                No answers yet. Upload sources, then ask a question.
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-md border bg-background p-3">
                  <div className="text-xs text-muted-foreground">Answer</div>
                  <div className="mt-2 whitespace-pre-wrap text-sm">{lastAnswer.answer}</div>
                </div>
                <div className="rounded-md border bg-background p-3">
                  <div className="text-xs text-muted-foreground">Sources</div>
                  <div className="mt-2 space-y-2">
                    {lastAnswer.sources.length === 0 ? (
                      <div className="text-sm text-muted-foreground">No sources returned.</div>
                    ) : (
                      lastAnswer.sources.map((s) => (
                        <button
                          key={String(s.chunk_id)}
                          className="flex w-full items-start justify-between gap-3 rounded-md border px-3 py-2 text-left hover:bg-accent"
                          onClick={() => setSelectedArtifactSha(s.artifact_sha256)}
                        >
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium">{s.path ?? truncateHash(s.artifact_sha256)}</p>
                            <p className="mt-1 text-xs text-muted-foreground">
                              score {(s.score ?? 0).toFixed(3)}
                            </p>
                          </div>
                          <div className="text-xs text-muted-foreground">Open</div>
                        </button>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
          <Separator />
          <div className="px-4 py-3">
            <div className="flex items-center gap-2">
              <input
                className="flex-1 rounded-md border bg-background px-3 py-2 text-sm outline-none"
                placeholder="Ask a question…"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    askMutation.mutate()
                  }
                }}
              />
              <input
                className="w-20 rounded-md border bg-background px-2 py-2 text-sm outline-none"
                type="number"
                min={1}
                max={50}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                title="Top K"
              />
              <Button onClick={() => askMutation.mutate()} disabled={busy}>
                Ask
              </Button>
            </div>
            <div className="mt-2 text-[11px] text-muted-foreground">
              Tip: press Cmd/Ctrl+Enter to ask.
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="col-span-3 flex h-full flex-col rounded-lg border bg-card">
          <div className="px-4 py-3">
            <h2 className="text-sm font-semibold">Preview</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Click a source or citation to preview.
            </p>
          </div>
          <Separator />
          <div className="flex-1 overflow-auto p-3">
            {!selectedArtifactSha ? (
              <div className="text-sm text-muted-foreground">Select a source to preview.</div>
            ) : (
              <ArtifactViewer sha256={selectedArtifactSha} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
