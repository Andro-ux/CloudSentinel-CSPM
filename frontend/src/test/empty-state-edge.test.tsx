import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EmptyState } from '../components/common/EmptyState'

describe('EmptyState edge cases', () => {
  it('renders without action', () => {
    render(<EmptyState />)
    expect(screen.getByText('NO DATA FOUND')).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('renders with empty title and description', () => {
    render(<EmptyState title="" description="" />)
    expect(screen.getByText('NO DATA FOUND')).toBeInTheDocument()
  })

  it('renders action as string', () => {
    render(<EmptyState action={<span>ACTION</span>} />)
    expect(screen.getByText('ACTION')).toBeInTheDocument()
  })
})
