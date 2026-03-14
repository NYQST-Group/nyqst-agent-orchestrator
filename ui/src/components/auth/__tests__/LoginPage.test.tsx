import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, useNavigate } from 'react-router-dom'
import { LoginPage } from '../LoginPage'
import { authApi, ApiError } from '@/api/auth'
import { useToast } from '@/hooks/use-toast'

// Mock dependencies
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: vi.fn(),
  }
})

vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    devBootstrap: vi.fn(),
    getCurrentUser: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(public status: number, public statusText: string, public body?: unknown) {
      super(`API Error: ${status} ${statusText}`)
      this.name = 'ApiError'
    }
  },
}))

const mockSetAccessToken = vi.fn()
const mockSetApiKey = vi.fn()
const mockLogout = vi.fn()

vi.mock('@/stores/auth-store', () => ({
  useAuthStore: Object.assign(
    vi.fn((selector) => {
      const mockState = {
        setAccessToken: mockSetAccessToken,
      }
      return selector ? selector(mockState) : mockSetAccessToken
    }),
    {
      getState: vi.fn(() => ({
        setApiKey: mockSetApiKey,
        logout: mockLogout,
      })),
      setState: vi.fn(),
    }
  ),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: vi.fn(),
}))

describe('LoginPage', () => {
  const mockNavigate = vi.fn()
  const mockToast = vi.fn()

  function renderLoginPage() {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>
      </QueryClientProvider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useNavigate).mockReturnValue(mockNavigate)
    vi.mocked(useToast).mockReturnValue({ toast: mockToast, dismiss: vi.fn(), toasts: [] })
  })

  it('test_renders_login_form', () => {
    renderLoginPage()

    expect(screen.getByPlaceholderText('your-organisation')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /open demo workspace/i })).toBeInTheDocument()
  })

  it('test_email_login_submits_and_navigates', async () => {
    const mockResponse = {
      access_token: 'token-123',
      token_type: 'Bearer',
      expires_in: 3600,
      tenant_id: 'tenant-1',
      user_id: 'user-1',
    }
    vi.mocked(authApi.login).mockResolvedValue(mockResponse)

    renderLoginPage()

    const tenantInput = screen.getByPlaceholderText('your-organisation')
    const emailInput = screen.getByPlaceholderText('you@example.com')
    const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(tenantInput, { target: { value: 'test-org' } })
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        tenant_slug: 'test-org',
      })
    })

    expect(mockSetAccessToken).toHaveBeenCalledWith('token-123', {
      userId: 'user-1',
      tenantId: 'tenant-1',
    })
    expect(mockNavigate).toHaveBeenCalledWith('/overview')
  })

  it('test_email_login_error_shows_toast', async () => {
    vi.mocked(authApi.login).mockRejectedValue(new ApiError(401, 'Unauthorized'))

    renderLoginPage()

    const tenantInput = screen.getByPlaceholderText('your-organisation')
    const emailInput = screen.getByPlaceholderText('you@example.com')
    const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(tenantInput, { target: { value: 'test-org' } })
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'wrong' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Login failed',
        description: 'Invalid credentials',
      })
    })

    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('test_demo_login_calls_dev_bootstrap', async () => {
    const mockResponse = {
      access_token: 'demo-token',
      token_type: 'Bearer',
      expires_in: 3600,
      tenant_id: 'demo-tenant',
      user_id: 'demo-user',
    }
    vi.mocked(authApi.devBootstrap).mockResolvedValue(mockResponse)

    renderLoginPage()

    const demoButton = screen.getByRole('button', { name: /open demo workspace/i })
    fireEvent.click(demoButton)

    await waitFor(() => {
      expect(authApi.devBootstrap).toHaveBeenCalled()
    })

    expect(mockSetAccessToken).toHaveBeenCalledWith('demo-token', {
      userId: 'demo-user',
      tenantId: 'demo-tenant',
    })
    expect(mockNavigate).toHaveBeenCalledWith('/overview')
  })

  it('test_demo_login_error_shows_toast', async () => {
    vi.mocked(authApi.devBootstrap).mockRejectedValue(new ApiError(404, 'Not Found'))

    renderLoginPage()

    const demoButton = screen.getByRole('button', { name: /open demo workspace/i })
    fireEvent.click(demoButton)

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Demo login unavailable',
        description: expect.stringContaining('DEBUG=true'),
      })
    })

    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('test_api_key_mode_toggle', () => {
    renderLoginPage()

    // Initially in email mode
    expect(screen.getByPlaceholderText('your-organisation')).toBeInTheDocument()

    // Click toggle to API key mode
    const toggleButton = screen.getByText('Use API key instead')
    fireEvent.click(toggleButton)

    // Should now show API key form
    expect(screen.getByPlaceholderText('int_xxxxxxxxxxxxxxxx')).toBeInTheDocument()
    expect(screen.queryByPlaceholderText('your-organisation')).not.toBeInTheDocument()

    // Toggle back
    const backButton = screen.getByText('Use workspace credentials instead')
    fireEvent.click(backButton)

    // Should be back to email form
    expect(screen.getByPlaceholderText('your-organisation')).toBeInTheDocument()
  })

  it('test_api_key_login_validates_and_navigates', async () => {
    const mockUser = {
      user_id: null,
      tenant_id: 'tenant-1',
      tenant_name: 'Test Tenant',
      role: null,
      scopes: ['read', 'write'],
      api_key_id: 'key-1',
    }
    vi.mocked(authApi.getCurrentUser).mockResolvedValue(mockUser)

    renderLoginPage()

    // Switch to API key mode
    fireEvent.click(screen.getByText('Use API key instead'))

    const apiKeyInput = screen.getByPlaceholderText('int_xxxxxxxxxxxxxxxx')
    const submitButton = screen.getByRole('button', { name: /continue with api key/i })

    fireEvent.change(apiKeyInput, { target: { value: 'int_test_key_123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(authApi.getCurrentUser).toHaveBeenCalled()
    })

    expect(mockNavigate).toHaveBeenCalledWith('/overview')
  })
})
