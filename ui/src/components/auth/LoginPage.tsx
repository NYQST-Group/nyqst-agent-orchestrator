/**
 * Login page component
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, FileStack, Loader2, ShieldCheck, Sparkles } from 'lucide-react'
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
      navigate('/overview')
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
      navigate('/overview')
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
      navigate('/overview')
    } catch (_error) {
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
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.25),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.15),_transparent_30%),linear-gradient(135deg,_#0f172a_0%,_#111827_45%,_#020617_100%)] text-white">
      <div className="mx-auto grid min-h-screen max-w-7xl items-center gap-10 px-6 py-10 lg:grid-cols-[1.1fr_0.9fr] lg:px-10">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.24em] text-white/70">
            <Sparkles className="h-3.5 w-3.5" />
            Intelli Studio
          </div>
          <h1 className="mt-6 text-4xl font-semibold leading-tight lg:text-5xl">
            Professional intelligence workflows,
            <span className="block text-white/70">without losing the evidence trail.</span>
          </h1>
          <p className="mt-4 max-w-xl text-base leading-7 text-white/70">
            Research across source libraries, keep outputs grounded, and move from investigation to deliverable in one workspace.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
              <ShieldCheck className="h-5 w-5 text-sky-300" />
              <div className="mt-3 text-sm font-medium">Trusted operating surface</div>
              <div className="mt-1 text-sm text-white/60">
                Live runs, source libraries, and context rails stay visible in the shell.
              </div>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
              <ArrowRight className="h-5 w-5 text-indigo-300" />
              <div className="mt-3 text-sm font-medium">Ready for demo flows</div>
              <div className="mt-1 text-sm text-white/60">
                Use demo login to open the seeded workspace and move straight into research.
              </div>
            </div>
          </div>
        </div>

        <div className="w-full max-w-lg justify-self-end">
          <div className="rounded-[2rem] border border-white/10 bg-white/95 p-8 text-slate-900 shadow-2xl shadow-black/30 backdrop-blur">
            <div className="mb-8 flex items-center justify-center gap-3">
              <div className="grid h-12 w-12 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
                <FileStack className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-semibold">Intelli</div>
                <div className="text-sm text-slate-500">Studio access</div>
              </div>
            </div>

            <h2 className="mb-2 text-xl font-semibold">
              {apiKeyMode ? 'Access with API key' : 'Sign in to your workspace'}
            </h2>
            <p className="mb-6 text-sm text-slate-500">
              {apiKeyMode
                ? 'Use a tenant-scoped key to open the studio without an email/password flow.'
                : 'Use workspace credentials, or jump into the demo environment for a guided walk-through.'}
            </p>

            {apiKeyMode ? (
              <form onSubmit={handleApiKeyLogin} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
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
                className="w-full text-sm text-slate-500 hover:text-slate-700"
                onClick={() => setApiKeyMode(false)}
              >
                Use workspace credentials instead
              </button>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Organisation ID
                </label>
                <input
                  type="text"
                  value={formData.tenant_slug}
                  onChange={(e) =>
                    setFormData({ ...formData, tenant_slug: e.target.value })
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="your-organisation"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Password
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
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
                className="w-full rounded-xl"
                disabled={isLoading}
                onClick={handleDemoLogin}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Starting demo...
                  </>
                ) : (
                  'Open Demo Workspace'
                )}
              </Button>

              <button
                type="button"
                className="w-full text-sm text-slate-500 hover:text-slate-700"
                onClick={() => setApiKeyMode(true)}
              >
                Use API key instead
              </button>
            </form>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
