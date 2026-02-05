/**
 * Tests for SourcesPanel component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

// Mock the useThreadSources hook
vi.mock('@/hooks/use-thread-sources', () => ({
  useThreadSources: vi.fn(),
}))

import { useThreadSources } from '@/hooks/use-thread-sources'
import { SourcesPanel } from './SourcesPanel'
import { SourcesProvider } from '@/contexts/SourcesContext'
import { makeAgentSource } from '@/test/factories'

const mockUseThreadSources = useThreadSources as ReturnType<typeof vi.fn>

function renderWithProvider(ui: React.ReactElement) {
  return render(<SourcesProvider>{ui}</SourcesProvider>)
}

describe('SourcesPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders placeholder when no sources', () => {
    mockUseThreadSources.mockReturnValue([])

    renderWithProvider(<SourcesPanel />)

    expect(
      screen.getByText('Sources will appear here when the assistant cites documents')
    ).toBeInTheDocument()
  })

  it('renders sources list when present', () => {
    const sources = [
      makeAgentSource({
        chunk_id: 'chunk-1',
        artifact_sha256: 'abc123',
        content: 'First source content',
        score: 0.95,
        path_hint: 'docs/guide.pdf',
      }),
      makeAgentSource({
        chunk_id: 'chunk-2',
        artifact_sha256: 'def456',
        content: 'Second source content',
        score: 0.82,
        path_hint: 'docs/reference.pdf',
      }),
    ]
    mockUseThreadSources.mockReturnValue(sources)

    renderWithProvider(<SourcesPanel />)

    // Check heading
    expect(screen.getByText('Sources (2)')).toBeInTheDocument()

    // Check that sources are rendered
    expect(screen.getByText('docs/guide.pdf')).toBeInTheDocument()
    expect(screen.getByText('docs/reference.pdf')).toBeInTheDocument()
    expect(screen.getByText(/First source content/)).toBeInTheDocument()
    expect(screen.getByText(/Second source content/)).toBeInTheDocument()

    // Check scores are displayed (rounded to percentage)
    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('82%')).toBeInTheDocument()
  })

  it('passes sources to SourcesSidebar correctly', () => {
    const sources = [
      makeAgentSource({
        chunk_id: 'chunk-1',
        artifact_sha256: 'test-sha',
        content: 'Test content',
        score: 0.9,
        path_hint: undefined, // No path hint, should show SHA
      }),
    ]
    mockUseThreadSources.mockReturnValue(sources)

    renderWithProvider(<SourcesPanel />)

    // Verify the source data is rendered - shows first 12 chars of SHA when no path_hint
    expect(screen.getByText('test-sha'.slice(0, 12))).toBeInTheDocument()
    expect(screen.getByText(/Test content/)).toBeInTheDocument()
  })

  it('handles empty sources array', () => {
    mockUseThreadSources.mockReturnValue([])

    renderWithProvider(<SourcesPanel />)

    // Should show placeholder
    expect(
      screen.getByText('Sources will appear here when the assistant cites documents')
    ).toBeInTheDocument()

    // Should not show sources heading
    expect(screen.queryByText(/Sources \(\d+\)/)).not.toBeInTheDocument()
  })

  it('renders multiple sources in correct order', () => {
    const sources = [
      makeAgentSource({ path_hint: 'file1.pdf', score: 0.95 }),
      makeAgentSource({ path_hint: 'file2.pdf', score: 0.90 }),
      makeAgentSource({ path_hint: 'file3.pdf', score: 0.85 }),
    ]
    mockUseThreadSources.mockReturnValue(sources)

    renderWithProvider(<SourcesPanel />)

    const sourceElements = screen.getAllByText(/file\d\.pdf/)
    expect(sourceElements).toHaveLength(3)
    expect(sourceElements[0]).toHaveTextContent('file1.pdf')
    expect(sourceElements[1]).toHaveTextContent('file2.pdf')
    expect(sourceElements[2]).toHaveTextContent('file3.pdf')
  })
})
