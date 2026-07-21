import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SecurityScoreCard } from '../components/common/SecurityScoreCard'

describe('SecurityScoreCard responsive behavior', () => {
  it('renders all sizes', () => {
    const { rerender } = render(<SecurityScoreCard score={80} grade="B" size="sm" />)
    expect(screen.getByText('80')).toBeInTheDocument()

    rerender(<SecurityScoreCard score={80} grade="B" size="md" />)
    expect(screen.getByText('80')).toBeInTheDocument()

    rerender(<SecurityScoreCard score={80} grade="B" size="lg" />)
    expect(screen.getByText('80')).toBeInTheDocument()
  })

  it('applies correct score colors', () => {
    const { rerender } = render(<SecurityScoreCard score={95} grade="A" />)
    expect(screen.getByText('95')).toHaveClass('text-retro-healthy')

    rerender(<SecurityScoreCard score={25} grade="F" />)
    expect(screen.getByText('25')).toHaveClass('text-retro-critical')
  })
})
