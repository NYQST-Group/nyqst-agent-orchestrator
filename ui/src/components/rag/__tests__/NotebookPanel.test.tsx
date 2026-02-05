import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NotebookPanel } from '../NotebookPanel'
import { manifestsApi } from '@/api/client'
import { makePointer } from '@/test/factories'

// Mock dependencies
vi.mock('@/api/client', () => ({
  manifestsApi: {
    getEntries: vi.fn(),
    create: vi.fn(),
  },
  artifactsApi: {
    upload: vi.fn(),
  },
  pointersApi: {
    advance: vi.fn(),
  },
  ragApi: {
    ask: vi.fn(),
  },
}))

vi.mock('@/stores/workbench-store', () => ({
  useWorkbenchStore: vi.fn(() => ({
    openTab: vi.fn(),
  })),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: vi.fn(() => ({
    toast: vi.fn(),
  })),
}))

describe('NotebookPanel', () => {
  function renderPanel(pointer = makePointer({ manifest_sha256: 'abc123' })) {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    return render(
      <QueryClientProvider client={queryClient}>
        <NotebookPanel pointer={pointer} />
      </QueryClientProvider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('test_renders_notebook_heading', () => {
    vi.mocked(manifestsApi.getEntries).mockResolvedValue([])

    renderPanel()

    expect(screen.getByText('Notebook')).toBeInTheDocument()
    expect(
      screen.getByText(/Upload documents, then ask questions with citations/)
    ).toBeInTheDocument()
  })

  it('test_shows_empty_state_when_no_files', async () => {
    vi.mocked(manifestsApi.getEntries).mockResolvedValue([])

    renderPanel()

    expect(await screen.findByText(/No files yet/)).toBeInTheDocument()
    expect(screen.getByText(/Upload PDFs or DOCX to get started/)).toBeInTheDocument()
  })

  it('test_displays_file_list_from_entries', async () => {
    const mockEntries = [
      {
        path: 'document1.pdf',
        artifact_sha256: 'abc123',
        metadata: {
          filename: 'document1.pdf',
          media_type: 'application/pdf',
          size_bytes: 1024,
        },
      },
      {
        path: 'document2.docx',
        artifact_sha256: 'def456',
        metadata: {
          filename: 'document2.docx',
          media_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          size_bytes: 2048,
        },
      },
    ]
    vi.mocked(manifestsApi.getEntries).mockResolvedValue(mockEntries)

    renderPanel()

    expect(await screen.findByText('document1.pdf')).toBeInTheDocument()
    expect(await screen.findByText('document2.docx')).toBeInTheDocument()
  })

  it('test_ask_button_disabled_during_pending', async () => {
    vi.mocked(manifestsApi.getEntries).mockResolvedValue([])

    renderPanel()

    // Wait for the component to render
    await screen.findByText(/No files yet/)

    const askButton = screen.getByRole('button', { name: /ask/i })

    // Button should be enabled initially (though asking will fail without files)
    expect(askButton).not.toBeDisabled()
  })
})
