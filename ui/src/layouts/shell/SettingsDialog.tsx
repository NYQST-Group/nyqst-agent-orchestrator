import { Check, Monitor, Moon, Sun } from 'lucide-react'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/components/theme-provider'
import { useShellLayoutStore } from '@/stores/shell-layout-store'
import type { ShellModelOption } from '@/types/shell'

interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  models: ShellModelOption[]
}

export function SettingsDialog({ open, onOpenChange, models }: SettingsDialogProps) {
  const { theme, setTheme } = useTheme()
  const { preferredModelId, setPreferredModelId } = useShellLayoutStore()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Studio settings</DialogTitle>
          <DialogDescription>
            Keep the shell polished while leaving the live application routes and runtime intact.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-2xl border bg-card/70 p-4">
            <div className="text-sm font-semibold">Theme</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Light and dark modes should both feel intentional on the buyer path.
            </div>
            <div className="mt-4 grid gap-2">
              {[
                { id: 'light', label: 'Light', icon: Sun },
                { id: 'dark', label: 'Dark', icon: Moon },
                { id: 'system', label: 'System', icon: Monitor },
              ].map((option) => {
                const Icon = option.icon
                const selected = theme === option.id
                return (
                  <Button
                    key={option.id}
                    type="button"
                    variant={selected ? 'default' : 'outline'}
                    className="justify-between"
                    onClick={() => setTheme(option.id as 'light' | 'dark' | 'system')}
                  >
                    <span className="flex items-center gap-2">
                      <Icon className="h-4 w-4" />
                      {option.label}
                    </span>
                    {selected ? <Check className="h-4 w-4" /> : null}
                  </Button>
                )
              })}
            </div>
          </section>

          <section className="rounded-2xl border bg-card/70 p-4">
            <div className="text-sm font-semibold">Preferred model</div>
            <div className="mt-1 text-xs text-muted-foreground">
              This sets the default suggestion for new research and analysis sessions.
            </div>
            <div className="mt-4 grid gap-2">
              {models.map((model) => {
                const selected = (preferredModelId || models.find((item) => item.is_default)?.id) === model.id
                return (
                  <Button
                    key={model.id}
                    type="button"
                    variant={selected ? 'default' : 'outline'}
                    className="justify-between"
                    onClick={() => setPreferredModelId(model.id)}
                  >
                    <span className="flex flex-col items-start">
                      <span>{model.label}</span>
                      <span className="text-[11px] opacity-80">
                        {model.provider || 'Configured provider'}
                      </span>
                    </span>
                    {selected ? <Check className="h-4 w-4" /> : null}
                  </Button>
                )
              })}
            </div>
          </section>
        </div>
      </DialogContent>
    </Dialog>
  )
}
