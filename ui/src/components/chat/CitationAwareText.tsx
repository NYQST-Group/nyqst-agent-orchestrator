/**
 * Custom text renderer for assistant messages that converts citation
 * patterns ([1], [2], etc.) into interactive CitationLink components.
 *
 * Used as assistantMessage.components.Text in ThreadConfig.
 */

import { useMessage } from '@assistant-ui/react'
import { CitationLink } from './CitationLink'

/**
 * Parse message content and replace citation patterns with CitationLink components.
 *
 * Matches patterns like [1], [2], [3] in the text and converts them to
 * clickable links that scroll to the corresponding source.
 */
export function CitationAwareText() {
  const message = useMessage()

  // Get the text content from the message
  const content = message.content
    .filter((part) => part.type === 'text')
    .map((part) => (part.type === 'text' ? part.text : ''))
    .join('')

  if (!content) {
    return null
  }

  // Regular expression to match citations like [1], [2], [3]
  // Matches only digits inside square brackets
  const citationRegex = /\[(\d+)\]/g

  const parts: Array<string | JSX.Element> = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  // Parse the text and replace citation patterns with CitationLink components
  // eslint-disable-next-line no-cond-assign
  while ((match = citationRegex.exec(content)) !== null) {
    const matchIndex = match.index
    const citationNumber = parseInt(match[1], 10)

    // Add text before the citation
    if (matchIndex > lastIndex) {
      parts.push(content.slice(lastIndex, matchIndex))
    }

    // Add the citation link
    parts.push(<CitationLink key={`citation-${matchIndex}`} index={citationNumber} />)

    lastIndex = matchIndex + match[0].length
  }

  // Add any remaining text after the last citation
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex))
  }

  return <>{parts}</>
}
