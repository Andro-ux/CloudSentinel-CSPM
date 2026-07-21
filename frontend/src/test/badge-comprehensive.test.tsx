import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from '../components/ui/badge'

describe('Badge comprehensive', () => {
  it('renders with default variant', () => {
    render(<Badge>Default</Badge>)
    expect(screen.getByText('Default')).toHaveClass('bg-retro-primary')
  })

  it('renders with secondary variant', () => {
    render(<Badge variant="secondary">Secondary</Badge>)
    expect(screen.getByText('Secondary')).toHaveClass('bg-retro-surface-alt')
  })

  it('renders with destructive variant', () => {
    render(<Badge variant="destructive">Destructive</Badge>)
    expect(screen.getByText('Destructive')).toHaveClass('bg-retro-critical')
  })

  it('renders with outline variant', () => {
    render(<Badge variant="outline">Outline</Badge>)
    expect(screen.getByText('Outline')).toHaveClass('border-retro-border')
  })

  it('renders risk variants', () => {
    const variants = ['critical', 'high', 'medium', 'low', 'healthy'] as const
    variants.forEach(variant => {
      render(<Badge variant={variant}>{variant.toUpperCase()}</Badge>)
      expect(screen.getByText(variant.toUpperCase())).toBeInTheDocument()
    })
  })

  it('applies custom className', () => {
    render(<Badge className="custom-class">Custom</Badge>)
    expect(screen.getByText('Custom')).toHaveClass('custom-class')
  })
})
