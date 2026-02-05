/**
 * Tests for MessageFeedback component.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

import { MessageFeedback } from './message-feedback'

// Mock the toast hook
const mockToast = vi.fn()
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: mockToast }),
}))

// Mock the conversations API
vi.mock('@/api/conversations', () => ({
  conversationsApi: {
    addFeedback: vi.fn().mockResolvedValue({ id: 'fb-1', rating: 'positive' }),
  },
}))

import { conversationsApi } from '@/api/conversations'

describe('MessageFeedback', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns null for user messages', () => {
    const { container } = render(
      <MessageFeedback conversationId="c-1" messageId="m-1" role="user" />
    )
    expect(container.innerHTML).toBe('')
  })

  it('renders thumbs up/down buttons for assistant messages', () => {
    render(
      <MessageFeedback conversationId="c-1" messageId="m-1" role="assistant" />
    )
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(2)
  })

  it('calls API on thumbs up click', async () => {
    render(
      <MessageFeedback conversationId="c-1" messageId="m-1" role="assistant" />
    )
    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[0]) // thumbs up

    await waitFor(() => {
      expect(conversationsApi.addFeedback).toHaveBeenCalledWith(
        'c-1', 'm-1', { rating: 'positive' }
      )
    })
  })

  it('disables buttons after selection', async () => {
    render(
      <MessageFeedback conversationId="c-1" messageId="m-1" role="assistant" />
    )
    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[0])

    await waitFor(() => {
      expect(buttons[0]).toBeDisabled()
      expect(buttons[1]).toBeDisabled()
    })
  })

  it('shows error notification on API failure', async () => {
    vi.mocked(conversationsApi.addFeedback).mockRejectedValueOnce(new Error('Server error'))

    render(
      <MessageFeedback conversationId="c-1" messageId="m-1" role="assistant" />
    )
    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[0]) // thumbs up

    // After API failure, should show error toast and buttons remain enabled
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Failed to submit feedback',
        description: 'Please try again',
      })
      expect(buttons[0]).not.toBeDisabled()
      expect(buttons[1]).not.toBeDisabled()
    })
  })

  it('handles 409 duplicate gracefully without error toast', async () => {
    const error409 = Object.assign(new Error('Conflict'), { status: 409 })
    vi.mocked(conversationsApi.addFeedback).mockRejectedValueOnce(error409)

    render(
      <MessageFeedback conversationId="c-1" messageId="m-1" role="assistant" />
    )
    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[1]) // thumbs down

    // 409 should be handled silently - no toast, buttons disabled (feedback accepted)
    await waitFor(() => {
      expect(mockToast).not.toHaveBeenCalled()
      expect(buttons[0]).toBeDisabled()
      expect(buttons[1]).toBeDisabled()
    })
  })
})
