/**
 * Thumbs up/down feedback on assistant messages.
 */

import { useState } from 'react'
import { ThumbsUp, ThumbsDown } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { conversationsApi } from '@/api/conversations'
import { useToast } from '@/hooks/use-toast'
import { cn } from '@/lib/utils'

interface MessageFeedbackProps {
  conversationId: string
  messageId: string
  role: string
}

export function MessageFeedback({ conversationId, messageId, role }: MessageFeedbackProps) {
  const [selected, setSelected] = useState<'positive' | 'negative' | null>(null)
  const { toast } = useToast()

  if (role !== 'assistant') return null

  const handleFeedback = async (rating: 'positive' | 'negative') => {
    if (selected) return // already submitted
    try {
      await conversationsApi.addFeedback(conversationId, messageId, { rating })
      setSelected(rating)
    } catch (error) {
      // Check if it's a 409 Conflict (duplicate feedback)
      const status = (error as any)?.status
      if (status === 409) {
        // Silently handle duplicate feedback
        setSelected(rating)
      } else {
        // Show error notification for other failures
        toast({
          variant: 'destructive',
          title: 'Failed to submit feedback',
          description: 'Please try again',
        })
      }
    }
  }

  return (
    <div className="mt-1 flex gap-1">
      <Button
        variant="ghost"
        size="icon"
        className={cn(
          'h-6 w-6',
          selected === 'positive' && 'text-green-600'
        )}
        onClick={() => handleFeedback('positive')}
        disabled={selected !== null}
      >
        <ThumbsUp className="h-3 w-3" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className={cn(
          'h-6 w-6',
          selected === 'negative' && 'text-red-600'
        )}
        onClick={() => handleFeedback('negative')}
        disabled={selected !== null}
      >
        <ThumbsDown className="h-3 w-3" />
      </Button>
    </div>
  )
}
