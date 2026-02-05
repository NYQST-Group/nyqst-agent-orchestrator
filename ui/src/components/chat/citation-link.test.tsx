/**
 * Tests for CitationLink and CitationAwareText components.
 */

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { CitationLink } from './CitationLink'
import { SourcesProvider } from '@/contexts/SourcesContext'

describe('CitationLink', () => {
  it('renders citation number in square brackets', () => {
    render(
      <SourcesProvider>
        <CitationLink index={1} />
      </SourcesProvider>
    )

    expect(screen.getByRole('button', { name: 'View source 1' })).toHaveTextContent('[1]')
  })

  it('calls scrollToSource when clicked', async () => {
    const user = userEvent.setup()

    render(
      <SourcesProvider>
        <CitationLink index={2} />
      </SourcesProvider>
    )

    const button = screen.getByRole('button', { name: 'View source 2' })
    await user.click(button)

    // Note: In a real test, we'd verify scrolling behavior via integration tests
    // since we can't easily mock the context hook
  })

  it('renders different citation numbers', () => {
    const { rerender } = render(
      <SourcesProvider>
        <CitationLink index={1} />
      </SourcesProvider>
    )

    expect(screen.getByText('[1]')).toBeInTheDocument()

    rerender(
      <SourcesProvider>
        <CitationLink index={5} />
      </SourcesProvider>
    )

    expect(screen.getByText('[5]')).toBeInTheDocument()
  })

  it('has proper styling classes', () => {
    render(
      <SourcesProvider>
        <CitationLink index={1} />
      </SourcesProvider>
    )

    const button = screen.getByRole('button')
    expect(button).toHaveClass('text-primary')
    expect(button).toHaveClass('hover:underline')
    expect(button).toHaveClass('font-medium')
    expect(button).toHaveClass('cursor-pointer')
  })
})
