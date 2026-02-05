import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useTourStore } from '@/stores/tour-store'
import { submitTourFeedback } from '@/api/tour-feedback'
import { TOUR_STEPS } from '@/tour/tour-steps'
import { Check, Star } from 'lucide-react'

export function TourFeedbackForm() {
  const { currentStepIndex, feedbackByStep, setFeedback, markSubmitted, submittedSteps } =
    useTourStore()
  const step = TOUR_STEPS[currentStepIndex]
  const existing = feedbackByStep[step.id]
  const isSubmitted = submittedSteps.has(step.id)

  const [text, setText] = useState(existing?.text ?? '')
  const [rating, setRating] = useState<number | undefined>(existing?.rating)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!text.trim() && rating === undefined) return
    setSubmitting(true)
    setFeedback(step.id, text, rating)
    await submitTourFeedback({
      stepId: step.id,
      text: text.trim(),
      rating,
      timestamp: new Date().toISOString(),
    })
    markSubmitted(step.id)
    setSubmitting(false)
  }

  if (isSubmitted) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 text-sm text-emerald-700">
        <Check className="h-4 w-4" />
        Feedback recorded — thank you!
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">{step.feedbackPrompt}</label>

      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            onClick={() => setRating(n)}
            className="rounded p-1 transition-colors hover:bg-muted"
            aria-label={`Rate ${n} out of 5`}
          >
            <Star
              className={`h-5 w-5 ${
                rating !== undefined && n <= rating
                  ? 'fill-amber-400 text-amber-400'
                  : 'text-muted-foreground'
              }`}
            />
          </button>
        ))}
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Your thoughts..."
        rows={3}
        className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />

      <Button size="sm" onClick={handleSubmit} disabled={submitting || (!text.trim() && rating === undefined)}>
        {submitting ? 'Submitting...' : 'Submit Feedback'}
      </Button>
    </div>
  )
}
