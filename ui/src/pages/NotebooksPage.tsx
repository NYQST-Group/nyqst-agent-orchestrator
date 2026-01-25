import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { BookOpen, Plus, RefreshCw } from 'lucide-react'

import { pointersApi } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/use-toast'

function formatWhen(iso: string): string {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

export function NotebooksPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const notebooksQuery = useQuery({
    queryKey: ['pointers', 'notebooks'],
    queryFn: () => pointersApi.list('notebooks'),
  })

  const notebooks = useMemo(() => notebooksQuery.data ?? [], [notebooksQuery.data])

  const createMutation = useMutation({
    mutationFn: async () => {
      const name = window.prompt('Notebook name:', `notebook-${new Date().toISOString().slice(0, 10)}`)
      if (!name) return null
      const trimmed = name.trim()
      if (!trimmed) return null
      return pointersApi.create({
        namespace: 'notebooks',
        name: trimmed,
        pointer_type: 'bundle',
        description: 'Notebook',
        metadata: {
          source: 'ui',
          module: 'docs',
          index: { enabled: true, profile: 'docs.default' },
        },
      })
    },
    onSuccess: async (created) => {
      if (!created) return
      await queryClient.invalidateQueries({ queryKey: ['pointers', 'notebooks'] })
      navigate(`/docs/${created.id}`)
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: 'Failed to create notebook',
        description: error instanceof Error ? error.message : 'Unknown error',
      })
    },
  })

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-semibold tracking-tight">Doc Intelligence</h1>
          </div>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
            Notebooks are versioned source bundles (pointer → manifest → artifacts). Upload files, index, and ask questions with citations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => notebooksQuery.refetch()}
            disabled={notebooksQuery.isFetching}
          >
            <RefreshCw className={notebooksQuery.isFetching ? 'mr-2 h-4 w-4 animate-spin' : 'mr-2 h-4 w-4'} />
            Refresh
          </Button>
          <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
            <Plus className="mr-2 h-4 w-4" />
            New notebook
          </Button>
        </div>
      </div>

      <div className="mt-6 rounded-xl border bg-card">
        <div className="flex items-center justify-between px-5 py-4">
          <h2 className="text-sm font-semibold">Your notebooks</h2>
          <span className="text-xs text-muted-foreground">{notebooks.length} total</span>
        </div>
        <Separator />

        {notebooksQuery.isLoading ? (
          <div className="px-5 py-10 text-sm text-muted-foreground">Loading…</div>
        ) : notebooks.length === 0 ? (
          <div className="px-5 py-10">
            <p className="text-sm text-muted-foreground">
              No notebooks yet. Create one to start uploading sources.
            </p>
            <div className="mt-4">
              <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
                <Plus className="mr-2 h-4 w-4" />
                Create your first notebook
              </Button>
            </div>
          </div>
        ) : (
          <div className="divide-y">
            {notebooks.map((n) => (
              <button
                key={n.id}
                className="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-accent"
                onClick={() => navigate(`/docs/${n.id}`)}
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{n.name}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Updated {formatWhen(n.updated_at)}
                    {n.manifest_sha256 ? ' · has sources' : ' · empty'}
                  </p>
                </div>
                <div className="text-xs text-muted-foreground">Open</div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
