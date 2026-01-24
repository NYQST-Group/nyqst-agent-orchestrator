/**
 * Login page component
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileStack, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth-store'
import { authApi, ApiError } from '@/api/auth'
import { useToast } from '@/hooks/use-toast'

export function LoginPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const setAccessToken = useAuthStore((s) => s.setAccessToken)

  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    tenant_slug: '',
  })
  const [apiKeyMode, setApiKeyMode] = useState(false)
  const [apiKey, setApiKey] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await authApi.login(formData)
      setAccessToken(response.access_token, {
        userId: response.user_id,
        tenantId: response.tenant_id,
      })
      navigate('/workbench')
    } catch (error) {
      const message =
        error instanceof ApiError
          ? 'Invalid credentials'
          : 'An error occurred'
      toast({
        variant: 'destructive',
        title: 'Login failed',
        description: message,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    setIsLoading(true)
    try {
      const response = await authApi.devBootstrap()
      setAccessToken(response.access_token, {
        userId: response.user_id,
        tenantId: response.tenant_id,
      })
      navigate('/workbench')
    } catch (error) {
      const description =
        error instanceof ApiError && error.status === 404
          ? 'Demo login is disabled on the server. Set DEBUG=true and restart the backend.'
          : 'Unable to use demo login. Check the server logs.'
      toast({
        variant: 'destructive',
        title: 'Demo login unavailable',
        description,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleApiKeyLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Validate API key by fetching current user
      const setApiKeyState = useAuthStore.getState().setApiKey
      setApiKeyState(apiKey)

      const user = await authApi.getCurrentUser()
      useAuthStore.setState({
        tenantId: user.tenant_id,
        tenantName: user.tenant_name,
        scopes: user.scopes,
      })
      navigate('/workbench')
    } catch (error) {
      useAuthStore.getState().logout()
      toast({
        variant: 'destructive',
        title: 'Invalid API key',
        description: 'Please check your API key and try again',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <FileStack className="h-10 w-10 text-primary" />
            <span className="text-2xl font-bold">Intelli</span>
          </div>

          <h1 className="text-xl font-semibold text-center mb-6">
            {apiKeyMode ? 'API Key Login' : 'Sign In'}
          </h1>

          {apiKeyMode ? (
            <form onSubmit={handleApiKeyLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="int_xxxxxxxxxxxxxxxx"
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Continue with API Key'
                )}
              </Button>

              <button
                type="button"
                className="w-full text-sm text-gray-500 hover:text-gray-700"
                onClick={() => setApiKeyMode(false)}
              >
                Use email login instead
              </button>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tenant
                </label>
                <input
                  type="text"
                  value={formData.tenant_slug}
                  onChange={(e) =>
                    setFormData({ ...formData, tenant_slug: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="your-organization"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                className="w-full"
                disabled={isLoading}
                onClick={handleDemoLogin}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Starting demo...
                  </>
                ) : (
                  'Demo Login'
                )}
              </Button>

              <button
                type="button"
                className="w-full text-sm text-gray-500 hover:text-gray-700"
                onClick={() => setApiKeyMode(true)}
              >
                Use API key instead
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-gray-400 text-sm mt-6">
          Document Intelligence Platform
        </p>
      </div>
    </div>
  )
}
