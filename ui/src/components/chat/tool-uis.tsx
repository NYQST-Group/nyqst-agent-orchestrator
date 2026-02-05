/**
 * Tool UI registrations for @assistant-ui/react.
 *
 * Uses makeAssistantToolUI for declarative tool rendering.
 * The '*' wildcard catches all tools not matched by specific handlers.
 *
 * The render components are exported for testing.
 */

import { makeAssistantToolUI } from '@assistant-ui/react'
import { CheckCircle2, Loader2, XCircle, Search } from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useState } from 'react'

/**
 * Tool status type used by @assistant-ui/react.
 * Exported for testing. Uses readonly to match library types.
 */
export type ToolStatus =
  | { readonly type: 'running' }
  | { readonly type: 'complete' }
  | { readonly type: 'incomplete'; readonly reason: string; readonly error?: unknown }
  | { readonly type: 'requires-action'; readonly reason: string }

/**
 * Props for GenericToolRender component.
 * Exported for testing.
 */
export interface GenericToolRenderProps {
  toolName: string
  args?: Record<string, unknown>
  result?: unknown
  status: ToolStatus
}

/**
 * Generic tool render component - testable without runtime context.
 */
export function GenericToolRender({ toolName, args, result, status }: GenericToolRenderProps) {
  const [isOpen, setIsOpen] = useState(false)
  const isLoading = status.type === 'running'
  const isError = status.type === 'incomplete' && status.reason === 'error'
  const isComplete = status.type === 'complete'

  // Safely convert result to string for display
  const resultString =
    result != null
      ? typeof result === 'string'
        ? result
        : JSON.stringify(result, null, 2)
      : null

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className="my-2 rounded-lg border bg-muted/50 p-2">
        <CollapsibleTrigger className="flex w-full items-center gap-2 text-sm hover:bg-muted/80 rounded p-1 -m-1">
          {isComplete && (
            <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" data-testid="icon-complete" />
          )}
          {isError && (
            <XCircle className="h-4 w-4 text-destructive flex-shrink-0" data-testid="icon-error" />
          )}
          {isLoading && (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground flex-shrink-0" data-testid="icon-loading" />
          )}
          <span className="font-mono text-xs truncate">{toolName}</span>
          <span className="text-[10px] text-muted-foreground ml-auto">
            {isComplete ? 'completed' : isError ? 'failed' : 'running...'}
          </span>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="mt-2 space-y-2 pl-6">
            {args && (
              <div>
                <span className="text-[10px] font-medium uppercase text-muted-foreground">
                  Input
                </span>
                <pre className="mt-1 overflow-auto rounded bg-background p-2 text-xs max-h-32">
                  {JSON.stringify(args, null, 2)}
                </pre>
              </div>
            )}
            {isComplete && resultString && (
              <div>
                <span className="text-[10px] font-medium uppercase text-muted-foreground">
                  Output
                </span>
                {typeof result === 'string' ? (
                  <div className="prose prose-sm dark:prose-invert max-w-none mt-1">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{resultString}</ReactMarkdown>
                  </div>
                ) : (
                  <pre className="mt-1 overflow-auto rounded bg-background p-2 text-xs max-h-48">
                    {resultString}
                  </pre>
                )}
              </div>
            )}
            {isError && <div className="text-xs text-destructive">Tool execution failed</div>}
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  )
}

// Generic tool UI for all tools (fallback) - wraps GenericToolRender
export const GenericToolUI = makeAssistantToolUI<Record<string, unknown>, unknown>({
  toolName: '*',
  render: ({ toolName, args, result, status }) => (
    <GenericToolRender toolName={toolName} args={args} result={result} status={status} />
  ),
})

/**
 * Props for SearchDocumentsRender component.
 * Exported for testing.
 */
export interface SearchDocumentsRenderProps {
  args?: { query?: string }
  result?: unknown
  status: ToolStatus
}

/**
 * Search documents render component - testable without runtime context.
 */
export function SearchDocumentsRender({ args, result, status }: SearchDocumentsRenderProps) {
  const isComplete = status.type === 'complete'
  const isLoading = status.type === 'running'
  const query = args?.query

  return (
    <div className="my-2 rounded-lg border bg-blue-50 dark:bg-blue-950/30 p-3">
      <div className="flex items-center gap-2 text-sm">
        {isComplete ? (
          <CheckCircle2 className="h-4 w-4 text-blue-500" data-testid="search-icon-complete" />
        ) : isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin text-blue-500" data-testid="search-icon-loading" />
        ) : (
          <Search className="h-4 w-4 text-blue-500" data-testid="search-icon-default" />
        )}
        <span className="font-medium">Searching documents</span>
        {query && <span className="text-muted-foreground truncate max-w-xs">for "{query}"</span>}
      </div>
      {isComplete && result != null && (
        <div className="mt-2 text-xs text-muted-foreground">Found relevant passages</div>
      )}
    </div>
  )
}

// Search documents tool - shows document results nicely
export const SearchDocumentsToolUI = makeAssistantToolUI<{ query?: string }, unknown>({
  toolName: 'search_documents',
  render: ({ args, result, status }) => (
    <SearchDocumentsRender args={args} result={result} status={status} />
  ),
})

// Export all tool UIs as an array for easy registration
export const toolUIs = [GenericToolUI, SearchDocumentsToolUI]
