/**
 * Auth guard component - protects routes requiring authentication
 */

import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  useEffect(() => {
    if (!isAuthenticated) {
      // Redirect to login, preserving the intended destination
      navigate('/login', { state: { from: location.pathname } })
    }
  }, [isAuthenticated, navigate, location])

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
