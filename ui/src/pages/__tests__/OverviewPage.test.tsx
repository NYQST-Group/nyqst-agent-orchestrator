import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { OverviewPage } from '../OverviewPage'

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <OverviewPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('OverviewPage', () => {
  it('renders the page heading', () => {
    renderPage()
    expect(screen.getByText('Overview')).toBeInTheDocument()
  })

  it('renders module cards', () => {
    renderPage()
    expect(screen.getByText('Source Library')).toBeInTheDocument()
    expect(screen.getByText('Research')).toBeInTheDocument()
    expect(screen.getByText('Decisions')).toBeInTheDocument()
  })

  it('shows guided tour button', () => {
    renderPage()
    expect(screen.getByText('Take the guided tour')).toBeInTheDocument()
  })

  it('renders stat cards section', () => {
    renderPage()
    expect(screen.getByText('Source libraries')).toBeInTheDocument()
    expect(screen.getByText('Live runs')).toBeInTheDocument()
    expect(screen.getByText('Testing cost')).toBeInTheDocument()
  })
})
