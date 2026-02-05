import { Routes, Route, Navigate, useParams } from 'react-router-dom'
import { Workbench } from '@/components/workbench/Workbench'
import { LoginPage } from '@/components/auth/LoginPage'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Toaster } from '@/components/ui/toaster'
import { useAuthStore } from '@/stores/auth-store'
import { NotebooksPage } from '@/pages/NotebooksPage'
import { NotebookPage } from '@/pages/NotebookPage'
import { AppShell } from '@/layouts/AppShell'
import { OverviewPage } from '@/pages/OverviewPage'
import { ResearchPage } from '@/pages/ResearchPage'
import { AnalysisPage } from '@/pages/AnalysisPage'
import { DecisionsPage } from '@/pages/DecisionsPage'
import { ClientsPage } from '@/pages/ClientsPage'
import { ProjectsPage } from '@/pages/ProjectsPage'

function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const isDemo = import.meta.env.VITE_DEMO_MODE === 'true'

  function LegacyNotebookRedirect() {
    const { id } = useParams()
    return <Navigate to={id ? `/docs/${id}` : '/docs'} replace />
  }

  return (
    <div className="h-screen w-screen overflow-hidden">
      <Routes>
        <Route
          path="/"
          element={
            <Navigate to={isAuthenticated || isDemo ? '/overview' : '/login'} replace />
          }
        />
        <Route path="/login" element={<LoginPage />} />

        {/* Product shell */}
        <Route
          element={
            <AuthGuard>
              <AppShell />
            </AuthGuard>
          }
        >
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/docs" element={<NotebooksPage />} />
          <Route path="/docs/:id" element={<NotebookPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/decisions" element={<DecisionsPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
        </Route>

        {/* Legacy routes */}
        <Route path="/notebooks" element={<Navigate to="/docs" replace />} />
        <Route path="/notebooks/:id" element={<LegacyNotebookRedirect />} />

        {/* Dev/workbench */}
        <Route
          path="/workbench/*"
          element={
            <AuthGuard>
              <Workbench />
            </AuthGuard>
          }
        />
        <Route path="/advanced" element={<Navigate to="/workbench" replace />} />
      </Routes>
      <Toaster />
    </div>
  )
}

export default App
