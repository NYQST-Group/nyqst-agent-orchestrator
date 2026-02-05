/**
 * Tests for SourcesSidebar component.
 */

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { SourcesSidebar, type AgentSource } from './SourcesSidebar'
import { SourcesProvider } from '@/contexts/SourcesContext'

function renderWithProvider(ui: React.ReactElement) {
  return render(<SourcesProvider>{ui}</SourcesProvider>)
}

function makeSource(overrides: Partial<AgentSource> = {}): AgentSource {
  return {
    chunk_id: 'chunk-1',
    artifact_sha256: 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd',
    chunk_index: 0,
    content: 'This is the source content.',
    score: 0.85,
    ...overrides,
  }
}

describe('SourcesSidebar', () => {
  describe('Empty state', () => {
    it('renders empty state message when no sources', () => {
      renderWithProvider(<SourcesSidebar sources={[]} />)

      expect(
        screen.getByText('Sources will appear here when the assistant cites documents')
      ).toBeInTheDocument()
    })

    it('does not render header when empty', () => {
      renderWithProvider(<SourcesSidebar sources={[]} />)

      expect(screen.queryByText(/Sources \(/)).not.toBeInTheDocument()
    })
  })

  describe('Populated state', () => {
    it('renders header with source count', () => {
      const sources = [makeSource(), makeSource({ chunk_id: 'chunk-2' })]
      renderWithProvider(<SourcesSidebar sources={sources} />)

      expect(screen.getByText('Sources (2)')).toBeInTheDocument()
    })

    it('renders source cards with index numbers', () => {
      const sources = [
        makeSource({ chunk_id: 'chunk-1' }),
        makeSource({ chunk_id: 'chunk-2' }),
      ]
      renderWithProvider(<SourcesSidebar sources={sources} />)

      expect(screen.getByText('[1]')).toBeInTheDocument()
      expect(screen.getByText('[2]')).toBeInTheDocument()
    })

    it('displays content preview when present', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ content: 'Important document content' })]} />)

      expect(screen.getByText('Important document content')).toBeInTheDocument()
    })

    it('does not render content paragraph when content is empty', () => {
      const { container } = renderWithProvider(<SourcesSidebar sources={[makeSource({ content: '' })]} />)

      // The source card should exist but without content paragraph
      expect(screen.getByText('[1]')).toBeInTheDocument()
      // There should be no text-muted-foreground paragraph for content
      const contentParagraphs = container.querySelectorAll('.text-muted-foreground.line-clamp-3')
      expect(contentParagraphs.length).toBe(0)
    })
  })

  describe('Path hint vs sha256 fallback', () => {
    it('displays path_hint when available', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ path_hint: 'documents/contract.pdf' })]} />)

      expect(screen.getByText('documents/contract.pdf')).toBeInTheDocument()
    })

    it('falls back to truncated sha256 when path_hint is absent', () => {
      const sha = 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd'
      renderWithProvider(<SourcesSidebar sources={[makeSource({ artifact_sha256: sha, path_hint: undefined })]} />)

      // Should show first 12 chars of sha256
      expect(screen.getByText('abc123def456')).toBeInTheDocument()
    })
  })

  describe('Score display and clamping', () => {
    it('displays score as percentage', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ score: 0.85 })]} />)

      expect(screen.getByText('85%')).toBeInTheDocument()
    })

    it('rounds score to nearest integer', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ score: 0.867 })]} />)

      expect(screen.getByText('87%')).toBeInTheDocument()
    })

    it('clamps score above 1 to 100%', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ score: 1.5 })]} />)

      expect(screen.getByText('100%')).toBeInTheDocument()
    })

    it('clamps negative score to 0%', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ score: -0.5 })]} />)

      expect(screen.getByText('0%')).toBeInTheDocument()
    })

    it('handles undefined score as 0%', () => {
      renderWithProvider(<SourcesSidebar sources={[makeSource({ score: undefined as unknown as number })]} />)

      expect(screen.getByText('0%')).toBeInTheDocument()
    })
  })
})
