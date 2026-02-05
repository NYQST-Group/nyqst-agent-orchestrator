/**
 * Tests for use-thread-sources hook.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'

// Mock @assistant-ui/react
vi.mock('@assistant-ui/react', () => ({
  useThread: vi.fn(),
}))

import { useThread } from '@assistant-ui/react'
import { useThreadSources } from './use-thread-sources'

const mockUseThread = useThread as ReturnType<typeof vi.fn>

describe('use-thread-sources', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns empty array when no tool calls', () => {
    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages: [] })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toEqual([])
  })

  it('returns empty array when messages array is empty', () => {
    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages: [] })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toEqual([])
  })

  it('extracts sources from search_documents tool result', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: JSON.stringify([
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                chunk_index: 0,
                content: 'Test content',
                score: 0.95,
                path_hint: 'docs/test.pdf',
              },
            ]),
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toHaveLength(1)
    expect(result.current[0]).toMatchObject({
      chunk_id: 'chunk-1',
      artifact_sha256: 'sha-abc',
      chunk_index: 0,
      content: 'Test content',
      score: 0.95,
      path_hint: 'docs/test.pdf',
    })
  })

  it('deduplicates sources by chunk_id', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: JSON.stringify([
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                chunk_index: 0,
                content: 'First occurrence',
                score: 0.95,
              },
            ]),
          },
        ],
      },
      {
        id: 'msg-2',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: JSON.stringify([
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                chunk_index: 0,
                content: 'Duplicate - should be ignored',
                score: 0.90,
              },
            ]),
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    // Should only have one source despite duplicates
    expect(result.current).toHaveLength(1)
    expect(result.current[0].content).toBe('First occurrence')
  })

  it('ignores non-search_documents tool calls', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'other_tool',
            result: JSON.stringify([
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                content: 'Should be ignored',
              },
            ]),
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toEqual([])
  })

  it('handles tool calls without results', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            // No result field
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toEqual([])
  })

  it('handles invalid JSON in tool result', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: 'invalid json {',
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toEqual([])
  })

  it('sorts sources by score descending', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: JSON.stringify([
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                chunk_index: 0,
                content: 'Low score',
                score: 0.5,
              },
              {
                chunk_id: 'chunk-2',
                artifact_sha256: 'sha-def',
                chunk_index: 0,
                content: 'High score',
                score: 0.95,
              },
              {
                chunk_id: 'chunk-3',
                artifact_sha256: 'sha-ghi',
                chunk_index: 0,
                content: 'Medium score',
                score: 0.75,
              },
            ]),
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toHaveLength(3)
    expect(result.current[0].score).toBe(0.95)
    expect(result.current[1].score).toBe(0.75)
    expect(result.current[2].score).toBe(0.5)
  })

  it('handles object result instead of JSON string', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: [
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                chunk_index: 0,
                content: 'Direct object result',
                score: 0.9,
              },
            ],
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toHaveLength(1)
    expect(result.current[0].content).toBe('Direct object result')
  })

  it('provides default values for missing fields', () => {
    const messages = [
      {
        id: 'msg-1',
        role: 'assistant',
        content: [
          {
            type: 'tool-call',
            toolName: 'search_documents',
            result: JSON.stringify([
              {
                chunk_id: 'chunk-1',
                artifact_sha256: 'sha-abc',
                // Missing chunk_index, content, score, path_hint
              },
            ]),
          },
        ],
      },
    ]

    mockUseThread.mockImplementation((selector: (state: any) => any) =>
      selector({ messages })
    )

    const { result } = renderHook(() => useThreadSources())

    expect(result.current).toHaveLength(1)
    expect(result.current[0]).toMatchObject({
      chunk_id: 'chunk-1',
      artifact_sha256: 'sha-abc',
      chunk_index: 0,
      content: '',
      score: 0,
      path_hint: undefined,
    })
  })
})
