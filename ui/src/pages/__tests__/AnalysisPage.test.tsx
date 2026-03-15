import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'

import { AnalysisPage } from '@/pages/AnalysisPage'
import {
  connectBoardNodes,
  moveBoardNode,
} from '@/components/analysis/analysis-canvas-state'
import {
  createBenchmarkBoard,
  createScenarioBoard,
} from '@/components/analysis/analysis-canvas-fixtures'

describe('AnalysisPage', () => {
  it('renders the analysis canvas shell and benchmark entry point', () => {
    render(
      <MemoryRouter>
        <AnalysisPage />
      </MemoryRouter>
    )

    expect(screen.getByRole('heading', { name: 'Analysis Canvas' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Load 200-node benchmark' })).toBeInTheDocument()
    expect(screen.getByTestId('analysis-node-count')).toHaveTextContent('6 nodes')
  })

  it('adds a note node from the toolbar', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <AnalysisPage />
      </MemoryRouter>
    )

    await user.click(screen.getByRole('button', { name: 'Add note' }))

    expect(screen.getByTestId('analysis-node-count')).toHaveTextContent('7 nodes')
  })
})

describe('analysis canvas state helpers', () => {
  it('moves nodes by id', () => {
    const board = createScenarioBoard()
    const moved = moveBoardNode(board.nodes, board.nodes[0].id, { x: 512, y: 384 })

    expect(moved[0].position).toEqual({ x: 512, y: 384 })
    expect(board.nodes[0].position).toEqual({ x: 80, y: 80 })
  })

  it('creates typed edges through the connection helper', () => {
    const board = createScenarioBoard()
    const edges = connectBoardNodes(
      board.edges,
      { source: board.nodes[1].id, target: board.nodes[4].id },
      'contradicts'
    )
    const createdEdge = edges.find(
      (edge) =>
        edge.source === board.nodes[1].id &&
        edge.target === board.nodes[4].id &&
        edge.data?.relation === 'contradicts'
    )

    expect(createdEdge?.data?.relation).toBe('contradicts')
    expect(createdEdge?.label).toBe('Contradicts')
  })

  it('builds the benchmark board with 200 seeded nodes', () => {
    const board = createBenchmarkBoard()

    expect(board.nodes).toHaveLength(200)
    expect(board.edges.length).toBeGreaterThan(199)
  })
})
