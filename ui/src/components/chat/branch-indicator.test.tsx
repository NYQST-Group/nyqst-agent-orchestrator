import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BranchIndicator } from './branch-indicator'

describe('BranchIndicator', () => {
  it('renders nothing when siblingCount is 1', () => {
    const { container } = render(
      <BranchIndicator
        siblingCount={1}
        currentIndex={0}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('renders nothing when siblingCount is 0', () => {
    const { container } = render(
      <BranchIndicator
        siblingCount={0}
        currentIndex={0}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('shows "1/3" format when siblingCount is 3', () => {
    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={0}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )
    expect(screen.getByText('1/3')).toBeInTheDocument()
  })

  it('shows "2/3" when currentIndex is 1', () => {
    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={1}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )
    expect(screen.getByText('2/3')).toBeInTheDocument()
  })

  it('calls onPrev when prev button is clicked', async () => {
    const user = userEvent.setup()
    const onPrev = vi.fn()

    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={1}
        onPrev={onPrev}
        onNext={vi.fn()}
      />
    )

    const prevButton = screen.getAllByRole('button')[0]
    await user.click(prevButton)
    expect(onPrev).toHaveBeenCalledTimes(1)
  })

  it('calls onNext when next button is clicked', async () => {
    const user = userEvent.setup()
    const onNext = vi.fn()

    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={1}
        onPrev={vi.fn()}
        onNext={onNext}
      />
    )

    const nextButton = screen.getAllByRole('button')[1]
    await user.click(nextButton)
    expect(onNext).toHaveBeenCalledTimes(1)
  })

  it('disables prev button when at first sibling', () => {
    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={0}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )

    const prevButton = screen.getAllByRole('button')[0]
    expect(prevButton).toBeDisabled()
  })

  it('disables next button when at last sibling', () => {
    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={2}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )

    const nextButton = screen.getAllByRole('button')[1]
    expect(nextButton).toBeDisabled()
  })

  it('enables both buttons when in the middle', () => {
    render(
      <BranchIndicator
        siblingCount={3}
        currentIndex={1}
        onPrev={vi.fn()}
        onNext={vi.fn()}
      />
    )

    const [prevButton, nextButton] = screen.getAllByRole('button')
    expect(prevButton).not.toBeDisabled()
    expect(nextButton).not.toBeDisabled()
  })
})
