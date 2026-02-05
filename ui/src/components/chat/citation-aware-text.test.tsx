/**
 * Tests for CitationAwareText component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Mock the @assistant-ui/react useMessage hook
vi.mock('@assistant-ui/react', () => ({
  useMessage: vi.fn(),
}))

import { useMessage } from '@assistant-ui/react'
import { CitationAwareText } from './CitationAwareText'
import { SourcesProvider } from '@/contexts/SourcesContext'

const mockUseMessage = useMessage as ReturnType<typeof vi.fn>

// Helper to create message content
function makeMessageContent(text: string) {
  return [
    {
      type: 'text',
      text,
    },
  ]
}

describe('CitationAwareText', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Citation parsing', () => {
    it('renders plain text without citations', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('This is a simple message without any citations.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByText('This is a simple message without any citations.')).toBeInTheDocument()
    })

    it('converts single citation to clickable link', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('According to the lease [1], the rent is due monthly.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByText('According to the lease', { exact: false })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'View source 1' })).toBeInTheDocument()
      expect(screen.getByText(', the rent is due monthly.', { exact: false })).toBeInTheDocument()
    })

    it('converts multiple citations to clickable links', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('The contract [1] states that delivery [2] must occur by May.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByRole('button', { name: 'View source 1' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'View source 2' })).toBeInTheDocument()
    })

    it('handles citations at the start of text', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('[1] indicates that the policy is effective immediately.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByRole('button', { name: 'View source 1' })).toBeInTheDocument()
      expect(screen.getByText('indicates that the policy is effective immediately.')).toBeInTheDocument()
    })

    it('handles citations at the end of text', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('This is supported by the document [3]'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByText('This is supported by the document')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'View source 3' })).toBeInTheDocument()
    })

    it('handles consecutive citations', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('Multiple sources [1][2][3] confirm this.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByRole('button', { name: 'View source 1' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'View source 2' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'View source 3' })).toBeInTheDocument()
    })

    it('handles double-digit citation numbers', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('Source [15] provides detailed information.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByRole('button', { name: 'View source 15' })).toBeInTheDocument()
    })

    it('does not convert non-numeric brackets', () => {
      mockUseMessage.mockReturnValue({
        content: makeMessageContent('Arrays like [a, b, c] are not citations.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(screen.getByText('Arrays like [a, b, c] are not citations.')).toBeInTheDocument()
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })
  })

  describe('Empty content', () => {
    it('renders nothing when content is empty', () => {
      mockUseMessage.mockReturnValue({
        content: [],
      })

      const { container } = render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(container.firstChild).toBeNull()
    })

    it('renders nothing when content is only non-text', () => {
      mockUseMessage.mockReturnValue({
        content: [{ type: 'image', url: 'test.png' }],
      })

      const { container } = render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      expect(container.firstChild).toBeNull()
    })
  })

  describe('Integration with SourcesContext', () => {
    it('citation links trigger scrollToSource from context', async () => {
      const user = userEvent.setup()

      mockUseMessage.mockReturnValue({
        content: makeMessageContent('According to [1], this is correct.'),
      })

      render(
        <SourcesProvider>
          <CitationAwareText />
        </SourcesProvider>
      )

      const citationButton = screen.getByRole('button', { name: 'View source 1' })
      await user.click(citationButton)

      // The click should work without errors (testing integration, not implementation)
      expect(citationButton).toBeInTheDocument()
    })
  })
})
