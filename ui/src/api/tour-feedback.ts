export interface TourFeedbackPayload {
  stepId: string
  text: string
  rating?: number
  timestamp: string
}

export async function submitTourFeedback(payload: TourFeedbackPayload): Promise<void> {
  await fetch('/api/tour/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
