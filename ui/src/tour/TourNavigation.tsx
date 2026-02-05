import { Button } from '@/components/ui/button'
import { useTourStore } from '@/stores/tour-store'
import { TOUR_STEPS } from '@/tour/tour-steps'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export function TourNavigation() {
  const { currentStepIndex, nextStep, prevStep } = useTourStore()
  const total = TOUR_STEPS.length
  const isFirst = currentStepIndex === 0
  const isLast = currentStepIndex === total - 1

  return (
    <div className="flex items-center justify-between">
      <Button variant="outline" size="sm" onClick={prevStep} disabled={isFirst}>
        <ChevronLeft className="mr-1 h-4 w-4" />
        Prev
      </Button>

      <div className="flex gap-1.5">
        {TOUR_STEPS.map((_, i) => (
          <div
            key={i}
            className={`h-2 w-2 rounded-full transition-colors ${
              i === currentStepIndex
                ? 'bg-primary'
                : i < currentStepIndex
                  ? 'bg-primary/40'
                  : 'bg-muted-foreground/20'
            }`}
          />
        ))}
      </div>

      <Button variant="outline" size="sm" onClick={nextStep} disabled={isLast}>
        Next
        <ChevronRight className="ml-1 h-4 w-4" />
      </Button>
    </div>
  )
}
