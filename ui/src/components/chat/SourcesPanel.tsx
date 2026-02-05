/**
 * Sources panel that extracts sources from thread tool calls.
 *
 * Must be rendered within AssistantRuntimeProvider context (inside ChatPanel).
 * Automatically extracts sources from search_documents tool results.
 */

import { SourcesSidebar } from './SourcesSidebar'
import { useThreadSources } from '@/hooks/use-thread-sources'

/**
 * SourcesPanel wrapper that extracts sources from the thread.
 *
 * Use this as the rightPanel prop in ChatPanel for Research module.
 */
export function SourcesPanel() {
  const sources = useThreadSources()

  return <SourcesSidebar sources={sources} />
}
