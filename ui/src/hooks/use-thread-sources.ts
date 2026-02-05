/**
 * Hook to extract sources from search_documents tool call results.
 *
 * Monitors the thread messages and extracts source data from completed
 * search_documents tool calls to display in the SourcesSidebar.
 */

import { useMemo } from 'react'
import { useThread } from '@assistant-ui/react'

import type { AgentSource } from '@/components/chat/SourcesSidebar'

/**
 * Type guard to check if a part is a tool-call with the expected shape.
 */
function isToolCallPart(
  part: unknown
): part is { type: 'tool-call'; toolName: string; result?: unknown } {
  return (
    typeof part === 'object' &&
    part !== null &&
    'type' in part &&
    (part as { type: unknown }).type === 'tool-call' &&
    'toolName' in part
  )
}

/**
 * Type guard for source item shape.
 */
function isSourceItem(
  item: unknown
): item is { chunk_id: unknown; artifact_sha256: unknown; [key: string]: unknown } {
  return (
    typeof item === 'object' &&
    item !== null &&
    'chunk_id' in item &&
    'artifact_sha256' in item
  )
}

/**
 * Extract sources from search_documents tool results in the thread.
 *
 * @returns Array of AgentSource objects from completed search_documents calls
 */
export function useThreadSources(): AgentSource[] {
  // Use selector to get messages - thread state has readonly messages array
  const messages = useThread((state) => state.messages)

  return useMemo(() => {
    if (!messages?.length) return []

    const sources: AgentSource[] = []
    const seenChunkIds = new Set<string>()

    // Iterate through all messages looking for tool call results
    for (const message of messages) {
      const content = message.content
      if (!content || !Array.isArray(content)) continue

      for (const part of content) {
        // Look for tool-call parts with results
        if (isToolCallPart(part) && part.toolName === 'search_documents' && part.result != null) {
          const result = part.result

          // Parse result - it's a JSON string from the tool
          let parsed: unknown
          if (typeof result === 'string') {
            try {
              parsed = JSON.parse(result)
            } catch {
              // Not valid JSON, might be error message
              continue
            }
          } else {
            parsed = result
          }

          // Extract sources array
          if (Array.isArray(parsed)) {
            for (const item of parsed) {
              if (isSourceItem(item)) {
                // Deduplicate by chunk_id
                const chunkKey = `${item.artifact_sha256}-${item.chunk_id}`
                if (!seenChunkIds.has(chunkKey)) {
                  seenChunkIds.add(chunkKey)
                  const score = item.score
                  const chunkIndex = item.chunk_index
                  sources.push({
                    chunk_id: String(item.chunk_id),
                    artifact_sha256: String(item.artifact_sha256),
                    chunk_index: typeof chunkIndex === 'number' ? chunkIndex : 0,
                    content: typeof item.content === 'string' ? item.content : '',
                    score: typeof score === 'number' ? score : 0,
                    path_hint: typeof item.path_hint === 'string' ? item.path_hint : undefined,
                  })
                }
              }
            }
          }
        }
      }
    }

    // Sort by score descending (most relevant first)
    return sources.sort((a, b) => b.score - a.score)
  }, [messages])
}
