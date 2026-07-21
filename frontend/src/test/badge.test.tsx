import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from '../components/ui/badge'

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Badge</Badge>)
    expect(screen.getByText('Badge')).toBeInTheDocument()
  })

  it('applies variant classes', () => {
    render(<Badge variant="destructive">Destructive</Badge>)
    expect(screen.getByText('Destructive')).toHaveClass('bg-retro-critical')
  })

  it('applies critical variant', () => {
    render(<Badge variant="critical">Critical</Badge>)
    expect(screen.getByText('Critical')).toHaveClass('text-retro-critical')
  })

  it('applies high variant', () => {
    render(<Badge variant="high">High</Badge>)
    expect(screen.getByText('High')).toHaveClass('text-retro-high')
  })

  it('applies medium variant', () => {
    render(<Badge variant="medium">Medium</Badge>)
    expect(screen.getByText('Medium')).toHaveClass('text-retro-medium')
  })

  it('applies low variant', () => {
    render(<Badge variant="low">Low</Badge>)
    expect(screen.getByText('Low')).toHaveClass('text-retro-low')
  })

  it('applies healthy variant', () => {
    render(<Badge variant="healthy">Healthy</Badge>)
    expect(screen.getByText('Healthy')).toHaveClass('text-retro-healthy')
  })
})
