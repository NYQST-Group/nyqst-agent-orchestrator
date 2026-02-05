/**
 * Sidebar displaying sources/citations from the research assistant.
 *
 * Shows document chunks with relevance scores that were used
 * to generate the assistant's response.
 */

import { useEffect, useRef } from 'react'
import { FileText } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { useSourcesContext } from '@/contexts/SourcesContext'
import { cn } from '@/lib/utils'

export interface AgentSource {
  chunk_id: string
  artifact_sha256: string
  chunk_index: number
  content: string
  score: number
  path_hint?: string
}

interface SourcesSidebarProps {
  sources: AgentSource[]
}

export function SourcesSidebar({ sources }: SourcesSidebarProps) {
  const context = useSourcesContext()
  const highlightedIndex = context?.highlightedIndex ?? null
  const sourceRefs = useRef<Map<number, HTMLDivElement>>(new Map())

  // Scroll to highlighted source when it changes
  useEffect(() => {
    if (highlightedIndex !== null) {
      const element = sourceRefs.current.get(highlightedIndex)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }, [highlightedIndex])
  if (sources.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground">
        Sources will appear here when the assistant cites documents
      </div>
    )
  }

  return (
    <div className="p-4 space-y-3">
      <h3 className="flex items-center gap-2 font-medium text-sm">
        <FileText className="h-4 w-4" />
        Sources ({sources.length})
      </h3>
      {sources.map((source, index) => {
        const sourceIndex = index + 1
        const isHighlighted = highlightedIndex === sourceIndex

        return (
          <div
            key={`${source.artifact_sha256}-${source.chunk_id}`}
            ref={(el) => {
              if (el) {
                sourceRefs.current.set(sourceIndex, el)
              } else {
                sourceRefs.current.delete(sourceIndex)
              }
            }}
            className={cn(
              'rounded-lg border bg-background p-3 text-sm transition-all',
              isHighlighted && 'ring-2 ring-primary ring-offset-2 ring-offset-background'
            )}
          >
            <div className="flex items-start gap-2">
              <span className="text-xs font-medium text-primary shrink-0">[{sourceIndex}]</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">
                  {source.path_hint || source.artifact_sha256.slice(0, 12)}
                </p>
                {source.content && (
                  <p className="mt-1 text-xs text-muted-foreground line-clamp-3">
                    {source.content}
                  </p>
                )}
              </div>
              <Badge variant="secondary" className="text-[10px] shrink-0">
                {Math.round(Math.min(100, Math.max(0, (source.score ?? 0) * 100)))}%
              </Badge>
            </div>
          </div>
        )
      })}
    </div>
  )
}
