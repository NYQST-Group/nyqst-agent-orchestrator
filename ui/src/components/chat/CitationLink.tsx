/**
 * Citation link component for inline source references.
 *
 * Renders a clickable citation (e.g., [1], [2]) that scrolls to
 * the corresponding source in the SourcesSidebar when clicked.
 */

import { useSourcesContext } from '@/contexts/SourcesContext'

interface CitationLinkProps {
  /**
   * The citation index (1-based).
   */
  index: number
}

/**
 * Clickable citation link that highlights and scrolls to a source.
 */
export function CitationLink({ index }: CitationLinkProps) {
  const context = useSourcesContext()

  const handleClick = () => {
    if (context?.scrollToSource) {
      context.scrollToSource(index)
    }
  }

  return (
    <button
      className="text-primary hover:underline font-medium cursor-pointer"
      onClick={handleClick}
      type="button"
      aria-label={`View source ${index}`}
    >
      [{index}]
    </button>
  )
}
