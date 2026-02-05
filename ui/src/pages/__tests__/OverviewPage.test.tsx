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
    expect(screen.getByText('Doc Intelligence')).toBeInTheDocument()
    expect(screen.getByText('Research Intelligence')).toBeInTheDocument()
    expect(screen.getByText('Decision Intelligence')).toBeInTheDocument()
  })

  it('shows guided tour button', () => {
    renderPage()
    expect(screen.getByText('Take a Guided Tour')).toBeInTheDocument()
  })

  it('renders stat cards section', () => {
    renderPage()
    expect(screen.getByText('Notebooks')).toBeInTheDocument()
    expect(screen.getByText('Trust surface')).toBeInTheDocument()
  })
})
