import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/card'

describe('Card comprehensive', () => {
  it('renders with default variant', () => {
    render(<Card>Content</Card>)
    const card = screen.getByText('Content')
    expect(card).toHaveClass('bg-retro-surface')
  })

  it('renders with hover variant', () => {
    render(<Card variant="hover">Hover</Card>)
    const card = screen.getByText('Hover')
    expect(card).toHaveClass('hover:shadow-retro')
  })

  it('renders with glow variant', () => {
    render(<Card variant="glow">Glow</Card>)
    const card = screen.getByText('Glow')
    expect(card).toHaveClass('border-retro-primary/30')
  })

  it('renders with flat variant', () => {
    render(<Card variant="flat">Flat</Card>)
    const card = screen.getByText('Flat')
    expect(card).toHaveClass('border-transparent')
  })

  it('renders CardHeader', () => {
    render(<CardHeader>Header</CardHeader>)
    expect(screen.getByText('Header')).toBeInTheDocument()
  })

  it('renders CardTitle', () => {
    render(<CardTitle>Title</CardTitle>)
    expect(screen.getByText('Title')).toBeInTheDocument()
  })

  it('renders CardContent', () => {
    render(<CardContent>Content</CardContent>)
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('renders CardFooter', () => {
    render(<CardFooter>Footer</CardFooter>)
    expect(screen.getByText('Footer')).toBeInTheDocument()
  })
})
