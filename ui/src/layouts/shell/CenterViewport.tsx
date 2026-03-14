import { Outlet } from 'react-router-dom'

export function CenterViewport() {
  return (
    <div className="h-full overflow-auto bg-background">
      <Outlet />
    </div>
  )
}
