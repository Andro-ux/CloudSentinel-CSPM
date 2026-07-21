import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from '../components/ui/button'

describe('Button comprehensive', () => {
  it('renders with default variant', () => {
    render(<Button>Default</Button>)
    const button = screen.getByText('Default')
    expect(button).toHaveClass('bg-retro-primary')
  })

  it('renders with secondary variant', () => {
    render(<Button variant="secondary">Secondary</Button>)
    const button = screen.getByText('Secondary')
    expect(button).toHaveClass('border-retro-primary')
  })

  it('renders with destructive variant', () => {
    render(<Button variant="destructive">Destructive</Button>)
    const button = screen.getByText('Destructive')
    expect(button).toHaveClass('bg-retro-critical')
  })

  it('renders with outline variant', () => {
    render(<Button variant="outline">Outline</Button>)
    const button = screen.getByText('Outline')
    expect(button).toHaveClass('border-retro-border')
  })

  it('renders with ghost variant', () => {
    render(<Button variant="ghost">Ghost</Button>)
    const button = screen.getByText('Ghost')
    expect(button).toHaveClass('hover:bg-retro-surface-alt')
  })

  it('renders with retro variant', () => {
    render(<Button variant="retro">Retro</Button>)
    const button = screen.getByText('Retro')
    expect(button).toHaveClass('font-retro')
  })

  it('renders different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    expect(screen.getByText('Small')).toHaveClass('h-9')

    rerender(<Button size="lg">Large</Button>)
    expect(screen.getByText('Large')).toHaveClass('h-11')
  })

  it('is disabled when disabled', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByText('Disabled')).toBeDisabled()
  })

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom</Button>)
    expect(screen.getByText('Custom')).toHaveClass('custom-class')
  })
})
