/**
 * Context for managing citation interactions between chat messages and sources.
 *
 * Provides scrollToSource function and tracks which source is highlighted
 * when a citation is clicked.
 */

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

interface SourcesContextValue {
  /**
   * The currently highlighted source index (1-based), or null if none.
   */
  highlightedIndex: number | null

  /**
   * Scroll to and highlight a specific source by its index (1-based).
   * @param index - Source index (1, 2, 3, etc.)
   */
  scrollToSource: (index: number) => void

  /**
   * Clear the highlight.
   */
  clearHighlight: () => void
}

const SourcesContext = createContext<SourcesContextValue | null>(null)

interface SourcesProviderProps {
  children: ReactNode
}

/**
 * Provider for citation-to-source linking functionality.
 *
 * Wrap ChatPanel or any component tree that needs citation
 * linking between messages and sources.
 */
export function SourcesProvider({ children }: SourcesProviderProps) {
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null)

  const scrollToSource = useCallback((index: number) => {
    setHighlightedIndex(index)
    // Clear highlight after 2 seconds
    setTimeout(() => setHighlightedIndex(null), 2000)
  }, [])

  const clearHighlight = useCallback(() => {
    setHighlightedIndex(null)
  }, [])

  return (
    <SourcesContext.Provider value={{ highlightedIndex, scrollToSource, clearHighlight }}>
      {children}
    </SourcesContext.Provider>
  )
}

/**
 * Hook to access citation-source linking context.
 * Returns null if not within a SourcesProvider (for backwards compatibility).
 */
export function useSourcesContext() {
  return useContext(SourcesContext)
}
