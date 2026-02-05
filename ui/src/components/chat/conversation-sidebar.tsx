/**
 * Sidebar listing conversations grouped by date.
 * Supports rename and delete via context menu.
 */

import { useMemo, useState, useRef, useEffect } from 'react'
import { MessageSquare, MoreHorizontal, Plus } from 'lucide-react'

import type { ConversationResponse } from '@/types/conversations'
import { conversationsApi } from '@/api/conversations'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { cn } from '@/lib/utils'

interface ConversationSidebarProps {
  conversations: ConversationResponse[]
  activeId: string | null
  onSelect: (id: string) => void
  onCreate: () => void
  onUpdate?: (id: string, updates: Partial<ConversationResponse>) => void
  onDelete?: (id: string) => void
}

function groupByDate(conversations: ConversationResponse[]) {
  const groups: Record<string, ConversationResponse[]> = {}
  const now = new Date()
  const today = now.toDateString()
  const yesterday = new Date(now.getTime() - 86400000).toDateString()

  for (const conv of conversations) {
    const date = new Date(conv.updated_at || conv.created_at)
    const dateStr = date.toDateString()
    let label: string
    if (dateStr === today) label = 'Today'
    else if (dateStr === yesterday) label = 'Yesterday'
    else label = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })

    if (!groups[label]) groups[label] = []
    groups[label].push(conv)
  }
  return groups
}

export function ConversationSidebar({
  conversations,
  activeId,
  onSelect,
  onCreate,
  onUpdate,
  onDelete,
}: ConversationSidebarProps) {
  const { toast } = useToast()
  const grouped = useMemo(() => groupByDate(conversations), [conversations])
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)
  const renameInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (renamingId) renameInputRef.current?.focus()
  }, [renamingId])

  const startRename = (conv: ConversationResponse) => {
    setRenamingId(conv.id)
    setRenameValue(conv.title || '')
  }

  const commitRename = async () => {
    if (!renamingId || !renameValue.trim()) {
      setRenamingId(null)
      return
    }
    try {
      await conversationsApi.update(renamingId, { title: renameValue.trim() })
      onUpdate?.(renamingId, { title: renameValue.trim() })
    } catch {
      toast({
        variant: 'destructive',
        title: 'Failed to rename conversation',
        description: 'Please try again',
      })
    }
    setRenamingId(null)
  }

  const confirmDelete = async () => {
    if (!deleteConfirmId) return
    try {
      await conversationsApi.delete(deleteConfirmId)
      onDelete?.(deleteConfirmId)
    } catch {
      toast({
        variant: 'destructive',
        title: 'Failed to delete conversation',
        description: 'Please try again',
      })
    }
    setDeleteConfirmId(null)
  }

  return (
    <div className="flex h-full w-64 flex-col border-r bg-muted/30">
      <div className="flex items-center justify-between border-b px-3 py-3">
        <span className="text-sm font-semibold">Conversations</span>
        <Button variant="ghost" size="icon" onClick={onCreate} className="h-7 w-7">
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-auto p-2">
        {conversations.length === 0 ? (
          <div className="px-3 py-8 text-center text-xs text-muted-foreground">
            No conversations yet. Start a new one!
          </div>
        ) : (
          Object.entries(grouped).map(([label, convs]) => (
            <div key={label} className="mb-3">
              <div className="mb-1 px-2 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                {label}
              </div>
              {convs.map((conv) => (
                <div
                  key={conv.id}
                  className={cn(
                    'group flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent',
                    activeId === conv.id && 'bg-accent'
                  )}
                >
                  <button
                    className="flex flex-1 items-center gap-2 overflow-hidden"
                    onClick={() => onSelect(conv.id)}
                  >
                    <MessageSquare className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    {renamingId === conv.id ? (
                      <input
                        ref={renameInputRef}
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        onBlur={commitRename}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') commitRename()
                          if (e.key === 'Escape') setRenamingId(null)
                        }}
                        className="w-full bg-transparent text-sm outline-none"
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <span className="truncate">
                        {conv.title || `Conversation ${conv.message_count} msgs`}
                      </span>
                    )}
                  </button>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button
                        className="shrink-0 opacity-0 group-hover:opacity-100"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-3.5 w-3.5 text-muted-foreground" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => startRename(conv)}>
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => setDeleteConfirmId(conv.id)}
                      >
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))}
            </div>
          ))
        )}
      </div>

      <AlertDialog open={!!deleteConfirmId} onOpenChange={() => setDeleteConfirmId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. The conversation and all its messages
              will be permanently deleted.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
