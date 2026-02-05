/**
 * Research page with AI-powered document Q&A.
 *
 * Uses ChatPanel for the chat experience with a sources sidebar
 * for displaying cited document passages.
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, ChevronDown, Loader2, MessageSquare, Sparkles } from 'lucide-react'

import type { Pointer } from '@/types/api'
import { pointersApi } from '@/api/client'
import { Button } from '@/components/ui/button'
import { ChatPanel } from '@/components/chat/ChatPanel'
import { SourcesPanel } from '@/components/chat/SourcesPanel'
import { useSessionLifecycle } from '@/hooks/use-session-lifecycle'
import { cn } from '@/lib/utils'

export function ResearchPage() {
  const [selectedPointerId, setSelectedPointerId] = useState<string | null>(null)
  const [showNotebookSelector, setShowNotebookSelector] = useState(false)

  // Session lifecycle (create on mount, idle on unmount)
  useSessionLifecycle('research')

  // Load notebooks (pointers with manifest)
  const pointersQuery = useQuery({
    queryKey: ['pointers'],
    queryFn: () => pointersApi.list(),
  })

  const notebooks = useMemo(() => {
    return (pointersQuery.data ?? []).filter((p) => p.manifest_sha256)
  }, [pointersQuery.data])

  const selectedNotebook: Pointer | undefined = useMemo(() => {
    if (!selectedPointerId) return undefined
    return notebooks.find((p) => p.id === selectedPointerId)
  }, [selectedPointerId, notebooks])

  return (
    <div className="flex h-full flex-col">
      {/* Header with notebook selector */}
      <header className="flex items-center justify-between border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <Sparkles className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Research Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Ask questions about your documents
            </p>
          </div>
        </div>

        <div className="relative">
          <Button
            variant="outline"
            className="min-w-[200px] justify-between"
            onClick={() => setShowNotebookSelector(!showNotebookSelector)}
          >
            <span className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              {selectedNotebook ? selectedNotebook.name : 'Select notebook'}
            </span>
            <ChevronDown className="h-4 w-4" />
          </Button>

          {showNotebookSelector && (
            <div className="absolute right-0 top-full z-50 mt-2 w-64 rounded-lg border bg-popover p-1 shadow-lg">
              {pointersQuery.isLoading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              ) : notebooks.length === 0 ? (
                <div className="px-3 py-4 text-center text-sm text-muted-foreground">
                  No notebooks with documents.
                  <br />
                  Upload files to a notebook first.
                </div>
              ) : (
                notebooks.map((notebook) => (
                  <button
                    key={notebook.id}
                    className={cn(
                      'flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-accent',
                      selectedPointerId === notebook.id && 'bg-accent'
                    )}
                    onClick={() => {
                      setSelectedPointerId(notebook.id)
                      setShowNotebookSelector(false)
                    }}
                  >
                    <BookOpen className="h-4 w-4 text-muted-foreground" />
                    <span className="truncate">{notebook.name}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>
      </header>

      {/* Chat area */}
      {selectedPointerId && selectedNotebook && selectedNotebook.manifest_sha256 ? (
        <ChatPanel
          module="research"
          scopeContext={{
            pointerId: selectedPointerId,
            manifestSha256: selectedNotebook.manifest_sha256,
          }}
          welcomeTitle="Research Assistant"
          welcomeMessage="Ask questions about your documents and get answers with citations."
          suggestions={[
            'What are the key terms?',
            'Summarize the main points',
            'What are the risk factors?',
          ]}
          rightPanel={<SourcesPanel />}
          className="flex-1"
        />
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <MessageSquare className="h-8 w-8 text-muted-foreground" />
          </div>
          <h2 className="mt-4 text-lg font-medium">Select a notebook to start</h2>
          <p className="mt-2 max-w-sm text-sm text-muted-foreground">
            Choose a notebook with uploaded documents to begin asking questions.
            The research assistant will search through your documents to find answers.
          </p>
        </div>
      )}
    </div>
  )
}
