import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Map } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useTourStore } from '@/stores/tour-store'
import { TOUR_STEPS } from '@/tour/tour-steps'
import { TourFeedbackForm } from '@/tour/TourFeedbackForm'
import { TourNavigation } from '@/tour/TourNavigation'

/** Simple inline bold rendering for **text** patterns from our static content */
function renderParagraph(text: string) {
  const parts = text.split(/\*\*(.*?)\*\*/g)
  return parts.map((part, i) =>
    i % 2 === 1 ? (
      <strong key={i} className="font-semibold text-foreground">
        {part}
      </strong>
    ) : (
      <span key={i}>{part}</span>
    )
  )
}

export function TourPanel() {
  const { isOpen, closeTour, currentStepIndex } = useTourStore()
  const navigate = useNavigate()
  const step = TOUR_STEPS[currentStepIndex]

  // Navigate to the step's route when step changes
  useEffect(() => {
    if (isOpen && step) {
      navigate(step.route)
    }
  }, [isOpen, currentStepIndex, step, navigate])

  if (!isOpen) return null

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex">
      {/* Backdrop */}
      <div className="w-screen flex-1 bg-black/20" onClick={closeTour} />

      {/* Panel */}
      <aside className="h-full w-[400px] shrink-0 overflow-y-auto border-l bg-background shadow-xl animate-in slide-in-from-right duration-300">
        <div className="flex h-full flex-col p-5">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-primary" />
              <span className="text-sm font-semibold">Guided Tour</span>
            </div>
            <Button variant="ghost" size="icon" onClick={closeTour} aria-label="Close tour">
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            Step {currentStepIndex + 1} of {TOUR_STEPS.length}
          </div>

          <Separator className="my-4" />

          {/* Step title */}
          <h2 className="text-lg font-semibold">{step.title}</h2>

          {/* Commentary */}
          <div className="mt-3 flex-1 space-y-2 text-sm leading-relaxed text-muted-foreground">
            {step.commentary.split('\n\n').map((para, i) => {
              if (para.startsWith('###')) return null
              if (para.startsWith('- ')) {
                const items = para.split('\n').filter((l) => l.startsWith('- '))
                return (
                  <ul key={i} className="list-disc space-y-1 pl-4">
                    {items.map((item, j) => (
                      <li key={j}>{renderParagraph(item.replace(/^- /, ''))}</li>
                    ))}
                  </ul>
                )
              }
              return <p key={i}>{renderParagraph(para)}</p>
            })}
          </div>

          <Separator className="my-4" />

          {/* Feedback */}
          <TourFeedbackForm />

          <Separator className="my-4" />

          {/* Navigation */}
          <TourNavigation />
        </div>
      </aside>
    </div>
  )
}
