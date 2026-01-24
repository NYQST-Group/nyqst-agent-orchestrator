import { Routes, Route, Navigate } from 'react-router-dom'
import { Workbench } from '@/components/workbench/Workbench'
import { LoginPage } from '@/components/auth/LoginPage'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Toaster } from '@/components/ui/toaster'
import { useAuthStore } from '@/stores/auth-store'

function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  return (
    <div className="h-screen w-screen overflow-hidden">
      <Routes>
        <Route
          path="/"
          element={
            <Navigate to={isAuthenticated ? '/workbench' : '/login'} replace />
          }
        />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/workbench/*"
          element={
            <AuthGuard>
              <Workbench />
            </AuthGuard>
          }
        />
      </Routes>
      <Toaster />
    </div>
  )
}

export default App
