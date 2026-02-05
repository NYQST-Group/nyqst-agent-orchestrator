import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  }
})

// Mock auth store
vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}))

describe('AuthGuard', () => {
  const mockNavigate = vi.fn()
  const mockLocation = { pathname: '/chat', search: '', hash: '', state: null, key: 'default' }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useNavigate).mockReturnValue(mockNavigate)
    vi.mocked(useLocation).mockReturnValue(mockLocation)
  })

  it('test_renders_children_when_authenticated', async () => {
    vi.mocked(useAuthStore).mockReturnValue(true)

    const { AuthGuard } = await import('../AuthGuard')

    render(
      <MemoryRouter>
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      </MemoryRouter>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('test_redirects_to_login_when_not_authenticated', async () => {
    vi.mocked(useAuthStore).mockReturnValue(false)

    const { AuthGuard } = await import('../AuthGuard')

    render(
      <MemoryRouter>
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      </MemoryRouter>
    )

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    expect(mockNavigate).toHaveBeenCalledWith('/login', {
      state: { from: '/chat' },
    })
  })

  it('test_preserves_return_path_in_location_state', async () => {
    vi.mocked(useAuthStore).mockReturnValue(false)
    const customLocation = { ...mockLocation, pathname: '/notebooks' }
    vi.mocked(useLocation).mockReturnValue(customLocation)

    const { AuthGuard } = await import('../AuthGuard')

    render(
      <MemoryRouter>
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      </MemoryRouter>
    )

    expect(mockNavigate).toHaveBeenCalledWith('/login', {
      state: { from: '/notebooks' },
    })
  })

  it('test_renders_children_in_demo_mode', async () => {
    // Set demo mode before importing the module
    vi.stubEnv('VITE_DEMO_MODE', 'true')

    // Clear the module cache and reimport
    vi.resetModules()
    const { AuthGuard } = await import('../AuthGuard')

    vi.mocked(useAuthStore).mockReturnValue(false)

    render(
      <MemoryRouter>
        <AuthGuard>
          <div>Demo Content</div>
        </AuthGuard>
      </MemoryRouter>
    )

    expect(screen.getByText('Demo Content')).toBeInTheDocument()
    expect(mockNavigate).not.toHaveBeenCalled()

    // Restore environment
    vi.unstubAllEnvs()
  })
})
