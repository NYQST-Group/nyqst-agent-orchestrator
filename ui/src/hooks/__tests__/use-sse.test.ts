import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSSE } from '../use-sse'

// Mock EventSource
class MockEventSource {
  static instances: MockEventSource[] = []
  url: string
  onopen: ((ev: Event) => void) | null = null
  onerror: ((ev: Event) => void) | null = null
  onmessage: ((ev: MessageEvent) => void) | null = null
  readyState = 0
  private listeners: Record<string, ((ev: MessageEvent) => void)[]> = {}

  constructor(url: string) {
    this.url = url
    MockEventSource.instances.push(this)
  }

  addEventListener(type: string, handler: (ev: MessageEvent) => void) {
    if (!this.listeners[type]) this.listeners[type] = []
    this.listeners[type].push(handler)
  }

  close() {
    this.readyState = 2
  }

  // Test helpers
  simulateOpen() {
    this.readyState = 1
    this.onopen?.(new Event('open'))
  }

  simulateMessage(data: string, lastEventId = '') {
    this.onmessage?.(new MessageEvent('message', { data, lastEventId }))
  }

  simulateError() {
    this.onerror?.(new Event('error'))
  }
}

beforeEach(() => {
  MockEventSource.instances = []
  vi.stubGlobal('EventSource', MockEventSource)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('useSSE', () => {
  it('starts in connecting state when enabled', () => {
    const { result } = renderHook(() =>
      useSSE({ url: '/test', enabled: true })
    )
    expect(result.current.status).toBe('connecting')
  })

  it('stays disconnected when disabled', () => {
    const { result } = renderHook(() =>
      useSSE({ url: '/test', enabled: false })
    )
    expect(result.current.status).toBe('disconnected')
  })

  it('transitions to connected on open', () => {
    const onConnect = vi.fn()
    const { result } = renderHook(() =>
      useSSE({ url: '/test', onConnect })
    )
    const es = MockEventSource.instances[0]

    act(() => es.simulateOpen())

    expect(result.current.status).toBe('connected')
    expect(onConnect).toHaveBeenCalled()
  })

  it('calls onEvent with parsed JSON data', () => {
    const onEvent = vi.fn()
    renderHook(() => useSSE({ url: '/test', onEvent }))
    const es = MockEventSource.instances[0]

    act(() => {
      es.simulateOpen()
      es.simulateMessage(JSON.stringify({ type: 'test' }))
    })

    expect(onEvent).toHaveBeenCalledWith('message', { type: 'test' })
  })

  it('disconnect closes EventSource', () => {
    const { result } = renderHook(() => useSSE({ url: '/test' }))
    const es = MockEventSource.instances[0]

    act(() => result.current.disconnect())

    expect(es.readyState).toBe(2)
    expect(result.current.status).toBe('disconnected')
  })
})
