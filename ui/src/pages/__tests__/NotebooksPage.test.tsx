import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { NotebooksPage } from '../NotebooksPage'

const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NotebooksPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('NotebooksPage', () => {
  it('renders page heading', () => {
    server.use(
      http.get('/api/v1/pointers', () => HttpResponse.json([]))
    )
    renderPage()
    expect(screen.getByText('Doc Intelligence')).toBeInTheDocument()
  })

  it('shows empty state when no notebooks', async () => {
    server.use(
      http.get('/api/v1/pointers', () => HttpResponse.json([]))
    )
    renderPage()
    await waitFor(() => {
      expect(screen.getByText(/No notebooks yet/)).toBeInTheDocument()
    })
  })

  it('shows create button', () => {
    server.use(
      http.get('/api/v1/pointers', () => HttpResponse.json([]))
    )
    renderPage()
    expect(screen.getByText('New notebook')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    server.use(
      http.get('/api/v1/pointers', async () => {
        await new Promise((r) => setTimeout(r, 5000))
        return HttpResponse.json([])
      })
    )
    renderPage()
    expect(screen.getByText(/Loading/)).toBeInTheDocument()
  })

  it('renders notebooks list when data returned', async () => {
    server.use(
      http.get('/api/v1/pointers', () =>
        HttpResponse.json([
          {
            id: '123',
            namespace: 'notebooks',
            name: 'test-notebook',
            pointer_type: 'bundle',
            manifest_sha256: 'abc',
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ])
      )
    )
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('test-notebook')).toBeInTheDocument()
    })
  })

  it('shows refresh button', () => {
    server.use(
      http.get('/api/v1/pointers', () => HttpResponse.json([]))
    )
    renderPage()
    expect(screen.getByText('Refresh')).toBeInTheDocument()
  })

  it('shows total count', async () => {
    server.use(
      http.get('/api/v1/pointers', () => HttpResponse.json([]))
    )
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('0 total')).toBeInTheDocument()
    })
  })
})
