/**
 * Message metadata footer component.
 *
 * Displays token count and latency for assistant messages.
 * Uses message metadata emitted via SSE stream.
 */

import { useMessage } from '@assistant-ui/react'

/**
 * Extended metadata interface for messages with usage stats.
 */
interface MessageMetadata {
  conversationId?: string
  userMessageId?: string
  assistantMessageId?: string
  outputTokens?: number
  latencyMs?: number
}

/**
 * Format latency for display.
 * Shows milliseconds as seconds with 1 decimal place.
 */
function formatLatency(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`
  }
  return `${(ms / 1000).toFixed(1)}s`
}

/**
 * Footer component that displays message metadata.
 * Used as assistantMessage.components.Footer in ThreadConfig.
 */
export function MessageMetadataFooter() {
  const message = useMessage()

  console.log('[MessageMetadata] Rendering for message:', message.id, 'role:', message.role, 'metadata:', message.metadata)

  // Only show for assistant messages
  if (message.role !== 'assistant') {
    return null
  }

  // Extract metadata from the message
  const metadata = message.metadata as MessageMetadata | undefined
  const outputTokens = metadata?.outputTokens
  const latencyMs = metadata?.latencyMs

  console.log('[MessageMetadata] Extracted - outputTokens:', outputTokens, 'latencyMs:', latencyMs)

  // Don't render if no metadata available
  if (!outputTokens && !latencyMs) {
    return null
  }

  const parts: string[] = []
  if (outputTokens !== undefined && outputTokens > 0) {
    parts.push(`${outputTokens} tokens`)
  }
  if (latencyMs !== undefined && latencyMs > 0) {
    parts.push(formatLatency(latencyMs))
  }

  if (parts.length === 0) {
    return null
  }

  return (
    <div className="mt-2 text-xs text-muted-foreground">
      {parts.join(' \u2022 ')}
    </div>
  )
}
