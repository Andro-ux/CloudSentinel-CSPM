import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SecurityScoreCard } from '../components/common/SecurityScoreCard'

describe('SecurityScoreCard comprehensive', () => {
  it('renders score and grade', () => {
    render(<SecurityScoreCard score={75} grade="B" />)
    expect(screen.getByText('75')).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
    expect(screen.getByText('SECURITY SCORE')).toBeInTheDocument()
  })

  it('applies healthy color for high scores', () => {
    render(<SecurityScoreCard score={95} grade="A" />)
    expect(screen.getByText('95')).toHaveClass('text-retro-healthy')
  })

  it('applies critical color for low scores', () => {
    render(<SecurityScoreCard score={15} grade="F" />)
    expect(screen.getByText('15')).toHaveClass('text-retro-critical')
  })

  it('applies medium color for medium scores', () => {
    render(<SecurityScoreCard score={45} grade="D" />)
    expect(screen.getByText('45')).toHaveClass('text-retro-high')
  })

  it('renders with custom label', () => {
    render(<SecurityScoreCard score={50} grade="C" label="CUSTOM LABEL" />)
    expect(screen.getByText('CUSTOM LABEL')).toBeInTheDocument()
  })

  it('renders small size', () => {
    render(<SecurityScoreCard score={50} grade="C" size="sm" />)
    expect(screen.getByText('50')).toBeInTheDocument()
  })

  it('renders large size', () => {
    render(<SecurityScoreCard score={50} grade="C" size="lg" />)
    expect(screen.getByText('50')).toBeInTheDocument()
  })
})
