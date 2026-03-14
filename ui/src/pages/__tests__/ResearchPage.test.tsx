/**
 * Tests for the ResearchPage component.
 *
 * Uses RTL for rendering, MSW for API mocking, and vitest for assertions.
 * Tests cover: initial state, notebook selection, and session lifecycle.
 *
 * Note: Many detailed chat interaction tests are now covered by the
 * @assistant-ui/react library's internal tests. We focus on integration
 * points specific to our implementation.
 */

import { describe, it, expect, beforeEach, afterEach, afterAll, beforeAll } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { ResearchPage } from '@/pages/ResearchPage'
import { useConversationStore } from '@/stores/conversation-store'
import { makePointer } from '@/test/factories'

// ---------------------------------------------------------------------------
// MSW server setup
// ---------------------------------------------------------------------------

const server = setupServer(
  http.get('/api/v1/pointers', () => {
    return HttpResponse.json([])
  }),
  http.get('/api/v1/conversations', () => {
    return HttpResponse.json({ items: [], total: 0 })
  }),
  http.post('/api/v1/sessions', () => {
    return HttpResponse.json({ id: 'sess-test-123', status: 'active', module: 'research' })
  }),
  http.patch('/api/v1/sessions/:id', () => {
    return HttpResponse.json({ id: 'sess-test-123', status: 'idle', module: 'research' })
  }),
  http.post('/api/v1/agent/chat', () => {
    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(encoder.encode('data: {"type":"start"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"start-step"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"text-start","id":"text-1"}\n\n'))
        controller.enqueue(
          encoder.encode(
            'data: {"type":"text-delta","id":"text-1","delta":"Test response from assistant"}\n\n'
          )
        )
        controller.enqueue(encoder.encode('data: {"type":"text-end","id":"text-1"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"finish-step"}\n\n'))
        controller.enqueue(encoder.encode('data: {"type":"finish"}\n\n'))
        controller.close()
      },
    })
    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'X-Run-Id': 'test-run-id',
        'X-Vercel-AI-UI-Message-Stream': 'v1',
      },
    })
  })
)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ResearchPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ResearchPage', () => {
  beforeEach(() => {
    // Clear the conversation store before each test
    useConversationStore.getState().clear()
  })

  describe('Initial State', () => {
    it('renders the page title', () => {
      renderPage()
      expect(screen.getByText('Research Workspace')).toBeInTheDocument()
    })

    it('shows notebook selector button', () => {
      renderPage()
      expect(screen.getByText('Select source library')).toBeInTheDocument()
    })

    it('shows prompt to select a notebook', () => {
      renderPage()
      expect(screen.getByText('Select a source library to start')).toBeInTheDocument()
    })

    it('does not show chat interface before notebook selection', () => {
      renderPage()
      // The chat interface (Thread/Composer) should not be rendered
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    })
  })

  describe('Notebook Selector', () => {
    it('opens dropdown on click', async () => {
      renderPage()
      const button = screen.getByText('Select source library')
      await userEvent.click(button)
      // Dropdown should now be visible (even if empty)
      await waitFor(() => {
        expect(screen.getByText(/No source libraries with documents/)).toBeInTheDocument()
      })
    })

    it('shows notebooks when available', async () => {
      const notebooks = [
        makePointer({ id: 'nb-1', name: 'Lease Agreement' }),
        makePointer({ id: 'nb-2', name: 'Financial Report' }),
      ]

      server.use(
        http.get('/api/v1/pointers', () => {
          return HttpResponse.json(notebooks)
        })
      )

      renderPage()
      const button = screen.getByText('Select source library')
      await userEvent.click(button)

      await waitFor(() => {
        expect(screen.getByText('Lease Agreement')).toBeInTheDocument()
        expect(screen.getByText('Financial Report')).toBeInTheDocument()
      })
    })

    it('selects notebook and shows chat interface', async () => {
      const notebooks = [makePointer({ id: 'nb-1', name: 'Test Notebook' })]

      server.use(
        http.get('/api/v1/pointers', () => {
          return HttpResponse.json(notebooks)
        })
      )

      renderPage()

      // Open selector and pick notebook
      await userEvent.click(screen.getByText('Select source library'))
      await waitFor(() => {
        expect(screen.getByText('Test Notebook')).toBeInTheDocument()
      })
      await userEvent.click(screen.getByText('Test Notebook'))

      // Chat interface should now be visible - look for the composer input
      // Note: @assistant-ui/react-ui Composer uses "Write a message..." as default,
      // but may use our configured "Ask a question..." if ThreadConfigProvider works
      await waitFor(() => {
        // Look for the Composer's input (it has a specific placeholder or role)
        const inputs = screen.getAllByRole('textbox')
        // At least one textbox should be present (the composer input)
        expect(inputs.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Session Lifecycle', () => {
    it('creates a session on mount', async () => {
      const sessionCreatedPromise = new Promise<string>((resolve) => {
        server.use(
          http.post('/api/v1/sessions', async ({ request }) => {
            const body = (await request.json()) as { module: string }
            resolve(body.module)
            return HttpResponse.json({ id: 'sess-new-123', status: 'active', module: 'research' })
          })
        )
      })

      renderPage()

      const module = await sessionCreatedPromise
      expect(module).toBe('research')
    })

    it('transitions session to idle on unmount', async () => {
      let resolveUpdate: ((value: boolean) => void) | null = null
      const sessionUpdatedPromise = new Promise<boolean>((resolve) => {
        resolveUpdate = resolve
      })

      server.use(
        http.post('/api/v1/sessions', () => {
          return HttpResponse.json({
            id: 'sess-lifecycle-456',
            status: 'active',
            module: 'research',
          })
        }),
        http.patch('/api/v1/sessions/:id', async ({ params, request }) => {
          const body = (await request.json()) as { status: string }
          if (params.id === 'sess-lifecycle-456' && body.status === 'idle') {
            resolveUpdate?.(true)
          }
          return HttpResponse.json({ id: params.id, status: 'idle', module: 'research' })
        })
      )

      const { unmount } = renderPage()

      // Wait for component to mount fully
      await waitFor(() => {
        expect(screen.getByText('Research Workspace')).toBeInTheDocument()
      })

      unmount()

      // Wait for the cleanup to fire and update the session
      const updated = await Promise.race([
        sessionUpdatedPromise,
        new Promise<boolean>((resolve) => setTimeout(() => resolve(false), 1000)),
      ])

      expect(updated).toBe(true)
    })

    it('handles session creation failure gracefully', async () => {
      server.use(
        http.post('/api/v1/sessions', () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      // Should not throw — page should still render
      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Research Workspace')).toBeInTheDocument()
      })
    })
  })

  describe('Sources Sidebar', () => {
    it('sources sidebar is visible but empty when notebook selected', async () => {
      const notebooks = [makePointer({ id: 'nb-1', name: 'Test Notebook' })]

      server.use(
        http.get('/api/v1/pointers', () => {
          return HttpResponse.json(notebooks)
        })
      )

      renderPage()
      await userEvent.click(screen.getByText('Select source library'))
      await waitFor(() => screen.getByText('Test Notebook'))
      await userEvent.click(screen.getByText('Test Notebook'))

      // Sources sidebar shows placeholder message
      await waitFor(() => {
        expect(
          screen.getByText('Sources will appear here when the assistant cites documents')
        ).toBeInTheDocument()
      })
    })
  })
})
