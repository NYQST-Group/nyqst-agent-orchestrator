/**
 * Tests for tool UI components.
 *
 * Tests the render components directly (GenericToolRender, SearchDocumentsRender)
 * since makeAssistantToolUI components need runtime context.
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

import {
  GenericToolRender,
  SearchDocumentsRender,
  GenericToolUI,
  SearchDocumentsToolUI,
  toolUIs,
} from './tool-uis'

describe('Tool UIs', () => {
  describe('Exports', () => {
    it('exports GenericToolUI component', () => {
      expect(GenericToolUI).toBeDefined()
    })

    it('exports SearchDocumentsToolUI component', () => {
      expect(SearchDocumentsToolUI).toBeDefined()
    })

    it('exports toolUIs array with correct length', () => {
      expect(toolUIs).toBeDefined()
      expect(Array.isArray(toolUIs)).toBe(true)
      expect(toolUIs.length).toBe(2)
    })

    it('exports GenericToolRender for testing', () => {
      expect(GenericToolRender).toBeDefined()
    })

    it('exports SearchDocumentsRender for testing', () => {
      expect(SearchDocumentsRender).toBeDefined()
    })
  })

  describe('GenericToolRender', () => {
    describe('Status indicators', () => {
      it('shows loading spinner when status is running', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            status={{ type: 'running' }}
          />
        )

        expect(screen.getByTestId('icon-loading')).toBeInTheDocument()
        expect(screen.getByText('running...')).toBeInTheDocument()
      })

      it('shows checkmark when status is complete', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            status={{ type: 'complete' }}
          />
        )

        expect(screen.getByTestId('icon-complete')).toBeInTheDocument()
        expect(screen.getByText('completed')).toBeInTheDocument()
      })

      it('shows error icon when status is incomplete with error reason', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            status={{ type: 'incomplete', reason: 'error' }}
          />
        )

        expect(screen.getByTestId('icon-error')).toBeInTheDocument()
        expect(screen.getByText('failed')).toBeInTheDocument()
      })
    })

    describe('Tool name display', () => {
      it('displays the tool name', () => {
        render(
          <GenericToolRender
            toolName="search_documents"
            status={{ type: 'running' }}
          />
        )

        expect(screen.getByText('search_documents')).toBeInTheDocument()
      })
    })

    describe('Collapsible behavior', () => {
      it('starts collapsed (args and result not visible)', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            args={{ query: 'test' }}
            result="The result"
            status={{ type: 'complete' }}
          />
        )

        // Collapsible content should be hidden initially (not in DOM)
        expect(screen.queryByText('Input')).not.toBeInTheDocument()
      })

      it('shows args and result when expanded', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            args={{ query: 'test' }}
            result="The result"
            status={{ type: 'complete' }}
          />
        )

        // Click the trigger to expand
        fireEvent.click(screen.getByRole('button'))

        // Now content should be visible
        expect(screen.getByText('Input')).toBeVisible()
        expect(screen.getByText('Output')).toBeVisible()
      })
    })

    describe('Args display', () => {
      it('shows JSON-formatted args when expanded', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            args={{ query: 'search term', limit: 10 }}
            status={{ type: 'running' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.getByText('Input')).toBeVisible()
        // Check that the args are JSON formatted
        expect(screen.getByText(/"query": "search term"/)).toBeInTheDocument()
        expect(screen.getByText(/"limit": 10/)).toBeInTheDocument()
      })

      it('does not show Input section when args is undefined', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            status={{ type: 'running' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.queryByText('Input')).not.toBeInTheDocument()
      })
    })

    describe('Result display', () => {
      it('shows string result with markdown rendering when complete', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            result="**Bold text** and _italic_"
            status={{ type: 'complete' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.getByText('Output')).toBeVisible()
        // Markdown should render the bold text
        expect(screen.getByText('Bold text')).toBeInTheDocument()
      })

      it('shows JSON-formatted object result when complete', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            result={{ found: 3, items: ['a', 'b', 'c'] }}
            status={{ type: 'complete' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.getByText('Output')).toBeVisible()
        expect(screen.getByText(/"found": 3/)).toBeInTheDocument()
      })

      it('does not show Output section when result is null', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            result={null}
            status={{ type: 'complete' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.queryByText('Output')).not.toBeInTheDocument()
      })

      it('does not show Output section when status is not complete', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            result="Some result"
            status={{ type: 'running' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.queryByText('Output')).not.toBeInTheDocument()
      })
    })

    describe('Error state', () => {
      it('shows error message when status is error', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            status={{ type: 'incomplete', reason: 'error' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.getByText('Tool execution failed')).toBeInTheDocument()
      })

      it('does not show error message for cancelled status', () => {
        render(
          <GenericToolRender
            toolName="test_tool"
            status={{ type: 'incomplete', reason: 'cancelled' }}
          />
        )

        fireEvent.click(screen.getByRole('button'))

        expect(screen.queryByText('Tool execution failed')).not.toBeInTheDocument()
      })
    })
  })

  describe('SearchDocumentsRender', () => {
    describe('Status indicators', () => {
      it('shows loading spinner when running', () => {
        render(
          <SearchDocumentsRender
            status={{ type: 'running' }}
          />
        )

        expect(screen.getByTestId('search-icon-loading')).toBeInTheDocument()
      })

      it('shows checkmark when complete', () => {
        render(
          <SearchDocumentsRender
            status={{ type: 'complete' }}
          />
        )

        expect(screen.getByTestId('search-icon-complete')).toBeInTheDocument()
      })

      it('shows search icon for other states', () => {
        render(
          <SearchDocumentsRender
            status={{ type: 'incomplete', reason: 'cancelled' }}
          />
        )

        expect(screen.getByTestId('search-icon-default')).toBeInTheDocument()
      })
    })

    describe('Title and query display', () => {
      it('always shows "Searching documents" text', () => {
        render(
          <SearchDocumentsRender
            status={{ type: 'running' }}
          />
        )

        expect(screen.getByText('Searching documents')).toBeInTheDocument()
      })

      it('shows query when provided', () => {
        render(
          <SearchDocumentsRender
            args={{ query: 'lease terms' }}
            status={{ type: 'running' }}
          />
        )

        expect(screen.getByText('for "lease terms"')).toBeInTheDocument()
      })

      it('does not show query text when query is undefined', () => {
        render(
          <SearchDocumentsRender
            status={{ type: 'running' }}
          />
        )

        expect(screen.queryByText(/for "/)).not.toBeInTheDocument()
      })
    })

    describe('Result display', () => {
      it('shows "Found relevant passages" when complete with result', () => {
        render(
          <SearchDocumentsRender
            result={[{ chunk_id: '1', content: 'test' }]}
            status={{ type: 'complete' }}
          />
        )

        expect(screen.getByText('Found relevant passages')).toBeInTheDocument()
      })

      it('does not show result message when running', () => {
        render(
          <SearchDocumentsRender
            result={[{ chunk_id: '1', content: 'test' }]}
            status={{ type: 'running' }}
          />
        )

        expect(screen.queryByText('Found relevant passages')).not.toBeInTheDocument()
      })

      it('does not show result message when result is null', () => {
        render(
          <SearchDocumentsRender
            result={null}
            status={{ type: 'complete' }}
          />
        )

        expect(screen.queryByText('Found relevant passages')).not.toBeInTheDocument()
      })
    })
  })
})
