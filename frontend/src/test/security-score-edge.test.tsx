import { describe, it, expect } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { SecurityScoreCard } from '../components/common/SecurityScoreCard'

describe('SecurityScoreCard edge cases', () => {
  it('renders with 0 score', () => {
    render(<SecurityScoreCard score={0} grade="F" />)
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('F')).toBeInTheDocument()
  })

  it('renders with 100 score', () => {
    render(<SecurityScoreCard score={100} grade="A" />)
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('A')).toBeInTheDocument()
  })

  it('renders with custom label', () => {
    render(<SecurityScoreCard score={50} grade="C" label="CUSTOM" />)
    expect(screen.getByText('CUSTOM')).toBeInTheDocument()
  })

  it('renders all sizes', () => {
    const sizes = ['sm', 'md', 'lg'] as const
    sizes.forEach(size => {
      cleanup()
      render(<SecurityScoreCard score={50} grade="C" size={size} />)
      expect(screen.getByText('50')).toBeInTheDocument()
    })
  })
})
