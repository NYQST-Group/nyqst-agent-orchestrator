import { create } from 'zustand'
import { TOUR_STEPS } from '@/tour/tour-steps'

interface TourState {
  isOpen: boolean
  currentStepIndex: number
  feedbackByStep: Record<string, { text: string; rating?: number }>
  submittedSteps: Set<string>

  // Actions
  openTour: () => void
  closeTour: () => void
  nextStep: () => void
  prevStep: () => void
  goToStep: (index: number) => void
  setFeedback: (stepId: string, text: string, rating?: number) => void
  markSubmitted: (stepId: string) => void
}

export const useTourStore = create<TourState>()((set) => ({
  isOpen: false,
  currentStepIndex: 0,
  feedbackByStep: {},
  submittedSteps: new Set(),

  openTour: () => set({ isOpen: true, currentStepIndex: 0 }),
  closeTour: () => set({ isOpen: false }),

  nextStep: () =>
    set((s) => ({
      currentStepIndex: Math.min(s.currentStepIndex + 1, TOUR_STEPS.length - 1),
    })),

  prevStep: () =>
    set((s) => ({
      currentStepIndex: Math.max(s.currentStepIndex - 1, 0),
    })),

  goToStep: (index) =>
    set({ currentStepIndex: Math.max(0, Math.min(index, TOUR_STEPS.length - 1)) }),

  setFeedback: (stepId, text, rating) =>
    set((s) => ({
      feedbackByStep: {
        ...s.feedbackByStep,
        [stepId]: { text, rating },
      },
    })),

  markSubmitted: (stepId) =>
    set((s) => {
      const next = new Set(s.submittedSteps)
      next.add(stepId)
      return { submittedSteps: next }
    }),
}))
