/**
 * SSE (Server-Sent Events) hooks for real-time updates
 */

import { useEffect, useRef, useCallback, useState } from 'react'

export type SSEStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

interface UseSSEOptions<T> {
  url: string
  onEvent?: (eventType: string, data: T) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  enabled?: boolean
  reconnectDelay?: number
  maxReconnectAttempts?: number
}

interface UseSSEResult {
  status: SSEStatus
  lastEventId: string | null
  reconnect: () => void
  disconnect: () => void
}

export function useSSE<T = unknown>({
  url,
  onEvent,
  onError,
  onConnect,
  enabled = true,
  reconnectDelay = 3000,
  maxReconnectAttempts = 5,
}: UseSSEOptions<T>): UseSSEResult {
  const [status, setStatus] = useState<SSEStatus>('disconnected')
  const [lastEventId, setLastEventId] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setStatus('disconnected')
  }, [])

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    setStatus('connecting')
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      setStatus('connected')
      reconnectAttemptsRef.current = 0
      onConnect?.()
    }

    eventSource.onerror = (error) => {
      setStatus('error')
      onError?.(error)

      // Auto-reconnect logic
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current++
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, reconnectDelay)
      } else {
        disconnect()
      }
    }

    // Handle generic message events
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as T
        setLastEventId(event.lastEventId)
        onEvent?.('message', data)
      } catch {
        // Handle non-JSON data
        onEvent?.('message', event.data as T)
      }
    }

    // Handle named events
    const handleNamedEvent = (eventType: string) => (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as T
        setLastEventId(event.lastEventId)
        onEvent?.(eventType, data)
      } catch {
        onEvent?.(eventType, event.data as T)
      }
    }

    // Common event types from our backend
    eventSource.addEventListener('connected', handleNamedEvent('connected'))
    eventSource.addEventListener('run_event', handleNamedEvent('run_event'))
    eventSource.addEventListener('activity', handleNamedEvent('activity'))
    eventSource.addEventListener('heartbeat', handleNamedEvent('heartbeat'))
    eventSource.addEventListener('error', handleNamedEvent('error'))
  }, [
    url,
    onEvent,
    onError,
    onConnect,
    reconnectDelay,
    maxReconnectAttempts,
    disconnect,
  ])

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0
    connect()
  }, [connect])

  useEffect(() => {
    if (enabled) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, connect, disconnect])

  return {
    status,
    lastEventId,
    reconnect,
    disconnect,
  }
}

/**
 * Hook specifically for streaming run events
 */
export function useRunEventStream(
  runId: string | null,
  onEvent: (event: {
    id: number
    run_id: string
    event_type: string
    payload: Record<string, unknown>
    timestamp: string
    duration_ms?: number
    sequence_num: number
  }) => void
) {
  const [events, setEvents] = useState<Array<{
    id: number
    run_id: string
    event_type: string
    payload: Record<string, unknown>
    timestamp: string
    duration_ms?: number
    sequence_num: number
  }>>([])

  const handleEvent = useCallback(
    (eventType: string, data: unknown) => {
      if (eventType === 'run_event') {
        const event = data as {
          id: number
          run_id: string
          event_type: string
          payload: Record<string, unknown>
          timestamp: string
          duration_ms?: number
          sequence_num: number
        }
        setEvents((prev) => [...prev, event])
        onEvent(event)
      }
    },
    [onEvent]
  )

  const { status, reconnect } = useSSE({
    url: runId ? `/api/v1/streams/runs/${runId}` : '',
    onEvent: handleEvent,
    enabled: !!runId,
  })

  const clearEvents = useCallback(() => {
    setEvents([])
  }, [])

  return {
    events,
    status,
    reconnect,
    clearEvents,
  }
}

/**
 * Hook for global activity feed
 */
export function useActivityStream(
  onActivity?: (data: {
    runs: Array<{
      type: string
      run_id: string
      run_type: string
      status: string
      created_at: string
    }>
  }) => void
) {
  const { status, reconnect } = useSSE<{
    runs: Array<{
      type: string
      run_id: string
      run_type: string
      status: string
      created_at: string
    }>
  }>({
    url: '/api/v1/streams/activity',
    onEvent: (eventType, data) => {
      if (eventType === 'activity' && onActivity) {
        onActivity(data)
      }
    },
  })

  return { status, reconnect }
}
