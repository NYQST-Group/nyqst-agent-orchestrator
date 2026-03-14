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
  inputTokens?: number
  outputTokens?: number
  costMicros?: number
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

function formatCost(costMicros: number): string {
  const usd = costMicros / 1_000_000
  if (usd === 0) return '$0.00'
  if (usd >= 0.01) {
    return `$${usd.toFixed(4)}`
  }
  return `$${usd.toFixed(6)}`.replace(/0+$/, '').replace(/\.$/, '')
}

/**
 * Footer component that displays message metadata.
 * Used as assistantMessage.components.Footer in ThreadConfig.
 */
export function MessageMetadataFooter() {
  const message = useMessage()

  // Only show for assistant messages
  if (message.role !== 'assistant') {
    return null
  }

  // Extract metadata from the message
  const metadata = message.metadata as MessageMetadata | undefined
  const inputTokens = metadata?.inputTokens
  const outputTokens = metadata?.outputTokens
  const costMicros = metadata?.costMicros
  const latencyMs = metadata?.latencyMs

  // Don't render if no metadata available
  if (!inputTokens && !outputTokens && !costMicros && !latencyMs) {
    return null
  }

  const parts: string[] = []
  if (inputTokens !== undefined && inputTokens > 0) {
    parts.push(`${inputTokens} in`)
  }
  if (outputTokens !== undefined && outputTokens > 0) {
    parts.push(`${outputTokens} out`)
  }
  if (costMicros !== undefined && costMicros > 0) {
    parts.push(formatCost(costMicros))
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
