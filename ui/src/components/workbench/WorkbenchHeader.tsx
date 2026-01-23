/**
 * Workbench header with navigation, panel toggles, and auth status
 */

import { useNavigate } from 'react-router-dom'
import {
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  PanelBottomClose,
  PanelBottomOpen,
  Settings,
  FileStack,
  LogOut,
  User,
  Building,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useWorkbenchStore } from '@/stores/workbench-store'
import { useAuthStore } from '@/stores/auth-store'
import { Separator } from '@/components/ui/separator'

export function WorkbenchHeader() {
  const navigate = useNavigate()
  const {
    leftPanelCollapsed,
    rightPanelCollapsed,
    bottomPanelCollapsed,
    toggleLeftPanel,
    toggleRightPanel,
    toggleBottomPanel,
  } = useWorkbenchStore()

  const { tenantName, role, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <TooltipProvider>
      <header className="flex h-12 items-center justify-between border-b bg-background px-4">
        {/* Left section - Logo and title */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <FileStack className="h-6 w-6 text-primary" />
            <span className="text-lg font-semibold">Intelli</span>
          </div>
          <Separator orientation="vertical" className="h-6" />
          {tenantName && (
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Building className="h-4 w-4" />
              <span>{tenantName}</span>
            </div>
          )}
        </div>

        {/* Center section - Activity indicator */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 rounded-md bg-muted px-3 py-1">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span className="text-xs text-muted-foreground">Connected</span>
          </div>
        </div>

        {/* Right section - Panel toggles, settings, and auth */}
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleLeftPanel}
                aria-label={
                  leftPanelCollapsed ? 'Show explorer' : 'Hide explorer'
                }
              >
                {leftPanelCollapsed ? (
                  <PanelLeftOpen className="h-4 w-4" />
                ) : (
                  <PanelLeftClose className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {leftPanelCollapsed ? 'Show explorer' : 'Hide explorer'}
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleBottomPanel}
                aria-label={
                  bottomPanelCollapsed ? 'Show timeline' : 'Hide timeline'
                }
              >
                {bottomPanelCollapsed ? (
                  <PanelBottomOpen className="h-4 w-4" />
                ) : (
                  <PanelBottomClose className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {bottomPanelCollapsed ? 'Show timeline' : 'Hide timeline'}
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleRightPanel}
                aria-label={
                  rightPanelCollapsed ? 'Show details' : 'Hide details'
                }
              >
                {rightPanelCollapsed ? (
                  <PanelRightOpen className="h-4 w-4" />
                ) : (
                  <PanelRightClose className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {rightPanelCollapsed ? 'Show details' : 'Hide details'}
            </TooltipContent>
          </Tooltip>

          <Separator orientation="vertical" className="mx-2 h-6" />

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Settings">
                <Settings className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Settings</TooltipContent>
          </Tooltip>

          <Separator orientation="vertical" className="mx-2 h-6" />

          {/* User info and logout */}
          {role && (
            <div className="flex items-center gap-1.5 px-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span className="capitalize">{role}</span>
            </div>
          )}

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                aria-label="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Sign out</TooltipContent>
          </Tooltip>
        </div>
      </header>
    </TooltipProvider>
  )
}
