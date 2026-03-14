/**
 * Tests for MessageMetadataFooter component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

// Mock the @assistant-ui/react useMessage hook
vi.mock('@assistant-ui/react', () => ({
  useMessage: vi.fn(),
}))

import { useMessage } from '@assistant-ui/react'
import { MessageMetadataFooter } from './message-metadata'

const mockUseMessage = useMessage as ReturnType<typeof vi.fn>

describe('MessageMetadataFooter', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing for user messages', () => {
    mockUseMessage.mockReturnValue({
      role: 'user',
      metadata: { outputTokens: 100, latencyMs: 500 },
    })

    const { container } = render(<MessageMetadataFooter />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when no metadata is present', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: undefined,
    })

    const { container } = render(<MessageMetadataFooter />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when metadata has no token or latency data', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: { conversationId: '123' },
    })

    const { container } = render(<MessageMetadataFooter />)
    expect(container.firstChild).toBeNull()
  })

  it('renders token count when available', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: { inputTokens: 120, outputTokens: 324 },
    })

    render(<MessageMetadataFooter />)
    expect(screen.getByText(/120 in.*324 out/)).toBeInTheDocument()
  })

  it('renders latency in milliseconds for short durations', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: { latencyMs: 500 },
    })

    render(<MessageMetadataFooter />)
    expect(screen.getByText('500ms')).toBeInTheDocument()
  })

  it('renders latency in seconds for longer durations', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: { latencyMs: 1200 },
    })

    render(<MessageMetadataFooter />)
    expect(screen.getByText('1.2s')).toBeInTheDocument()
  })

  it('renders both token count and latency separated by bullet', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: { inputTokens: 120, outputTokens: 324, costMicros: 456, latencyMs: 1200 },
    })

    render(<MessageMetadataFooter />)
    // The bullet character is \u2022
    expect(screen.getByText(/120 in.*324 out.*\$0\.000456.*1\.2s/)).toBeInTheDocument()
  })

  it('does not render zero token counts', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant',
      metadata: { outputTokens: 0, latencyMs: 1200 },
    })

    render(<MessageMetadataFooter />)
    expect(screen.getByText('1.2s')).toBeInTheDocument()
    expect(screen.queryByText('0 tokens')).not.toBeInTheDocument()
  })

  it('does not render zero latency', () => {
    mockUseMessage.mockReturnValue({
      role: 'assistant', metadata: { outputTokens: 100, latencyMs: 0 },
    })

    render(<MessageMetadataFooter />)
    expect(screen.getByText('100 out')).toBeInTheDocument()
    expect(screen.queryByText('0ms')).not.toBeInTheDocument()
  })
})
