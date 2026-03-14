/**
 * Tests for RunTimeline component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock the API client
vi.mock('@/api/client', () => ({
  runsApi: {
    get: vi.fn(),
    getEvents: vi.fn(),
  },
}))

// Mock the SSE hook
vi.mock('@/hooks/use-sse', () => ({
  useRunEventStream: vi.fn(),
}))

import { runsApi } from '@/api/client'
import { useRunEventStream } from '@/hooks/use-sse'
import { RunTimeline } from './RunTimeline'
import type { Run, RunEvent } from '@/types/api'

const mockRunsApi = vi.mocked(runsApi)
const mockUseRunEventStream = vi.mocked(useRunEventStream)

function makeRun(overrides: Partial<Run> = {}): Run {
  return {
    id: 'run-123',
    run_type: 'rag_index',
    name: 'Test Run',
    status: 'completed',
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    input_manifest_sha256: null,
    output_manifest_sha256: null,
    config: {},
    result: null,
    error: null,
    token_usage: {},
    cost_cents: 0,
    created_at: new Date().toISOString(),
    created_by: null,
    project_id: null,
    session_id: null,
    parent_run_id: null,
    ...overrides,
  }
}

function makeRunEvent(overrides: Partial<RunEvent> = {}): RunEvent {
  return {
    id: 1,
    run_id: 'run-123',
    event_type: 'run_started',
    payload: {},
    timestamp: new Date().toISOString(),
    duration_ms: undefined,
    sequence_num: 1,
    ...overrides,
  }
}

describe('RunTimeline', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    vi.clearAllMocks()
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    })

    // Default mock returns
    mockRunsApi.get.mockResolvedValue(makeRun())
    mockRunsApi.getEvents.mockResolvedValue([])
    mockUseRunEventStream.mockReturnValue({
      events: [],
      status: 'disconnected',
      reconnect: vi.fn(),
      clearEvents: vi.fn(),
    })
  })

  function renderWithQuery(ui: React.ReactElement) {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    )
  }

  it('renders loading state', () => {
    // Keep the promise pending to show loading state
    mockRunsApi.getEvents.mockReturnValue(new Promise(() => {}))

    const { container } = renderWithQuery(<RunTimeline runId="run-123" />)

    // Find the loading spinner by class
    const loader = container.querySelector('.animate-spin')
    expect(loader).toBeInTheDocument()
  })

  it('renders empty state when no events', async () => {
    mockRunsApi.getEvents.mockResolvedValue([])

    renderWithQuery(<RunTimeline runId="run-123" />)

    const emptyMessage = await screen.findByText('No events recorded yet')
    expect(emptyMessage).toBeInTheDocument()
  })

  it('renders events list when data present', async () => {
    const events = [
      makeRunEvent({ id: 1, event_type: 'run_started', sequence_num: 1 }),
      makeRunEvent({
        id: 2,
        event_type: 'tool_call_started',
        sequence_num: 2,
        payload: { tool_name: 'search_documents' }
      }),
      makeRunEvent({ id: 3, event_type: 'run_completed', sequence_num: 3 }),
    ]
    mockRunsApi.getEvents.mockResolvedValue(events)

    renderWithQuery(<RunTimeline runId="run-123" />)

    // Check that events are rendered
    expect(await screen.findByText('Run Started')).toBeInTheDocument()
    expect(await screen.findByText('search_documents')).toBeInTheDocument()
    expect(await screen.findByText('Completed')).toBeInTheDocument()
  })

  it('shows token and cost summary when run usage is present', async () => {
    mockRunsApi.get.mockResolvedValue(
      makeRun({
        token_usage: {
          'gpt-5-nano': {
            input_tokens: 120,
            output_tokens: 324,
            cost_micros: 456,
          },
        },
      })
    )
    mockRunsApi.getEvents.mockResolvedValue([
      makeRunEvent({ id: 1, event_type: 'llm_request', sequence_num: 1 }),
      makeRunEvent({ id: 2, event_type: 'llm_response', sequence_num: 2 }),
    ])

    renderWithQuery(<RunTimeline runId="run-123" />)

    expect(await screen.findByText('120 in · 324 out')).toBeInTheDocument()
    expect(screen.getByText('$0.000456')).toBeInTheDocument()
  })

  it('shows live indicator when run is active', async () => {
    const activeRun = makeRun({ status: 'running' })
    mockRunsApi.get.mockResolvedValue(activeRun)
    mockRunsApi.getEvents.mockResolvedValue([
      makeRunEvent({ id: 1, event_type: 'run_started', sequence_num: 1 }),
    ])
    mockUseRunEventStream.mockReturnValue({
      events: [],
      status: 'connected',
      reconnect: vi.fn(),
      clearEvents: vi.fn(),
    })

    renderWithQuery(<RunTimeline runId="run-123" />)

    // Check for live indicator
    expect(await screen.findByText('Live')).toBeInTheDocument()
  })

  it('calls SSE hook with runId when run is active', async () => {
    const activeRun = makeRun({ status: 'running' })
    mockRunsApi.get.mockResolvedValue(activeRun)
    mockRunsApi.getEvents.mockResolvedValue([])
    mockUseRunEventStream.mockReturnValue({
      events: [],
      status: 'connecting',
      reconnect: vi.fn(),
      clearEvents: vi.fn(),
    })

    renderWithQuery(<RunTimeline runId="run-123" />)

    // Wait for component to render
    await screen.findByText('No events recorded yet')

    // Verify SSE hook was called with the run ID
    expect(mockUseRunEventStream).toHaveBeenCalledWith(
      'run-123',
      expect.any(Function)
    )
  })

  it('does not call SSE hook when run is completed', async () => {
    const completedRun = makeRun({ status: 'completed' })
    mockRunsApi.get.mockResolvedValue(completedRun)
    mockRunsApi.getEvents.mockResolvedValue([])

    renderWithQuery(<RunTimeline runId="run-123" />)

    await screen.findByText('No events recorded yet')

    // SSE hook should be called with null when run is not running
    expect(mockUseRunEventStream).toHaveBeenCalledWith(
      null,
      expect.any(Function)
    )
  })
})
