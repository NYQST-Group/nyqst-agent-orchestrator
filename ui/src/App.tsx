import { Routes, Route, Navigate } from 'react-router-dom'
import { Workbench } from '@/components/workbench/Workbench'
import { Toaster } from '@/components/ui/toaster'

function App() {
  return (
    <div className="h-screen w-screen overflow-hidden">
      <Routes>
        <Route path="/" element={<Navigate to="/workbench" replace />} />
        <Route path="/workbench/*" element={<Workbench />} />
      </Routes>
      <Toaster />
    </div>
  )
}

export default App
