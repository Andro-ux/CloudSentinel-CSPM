import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EmptyState } from '../components/common/EmptyState'

describe('EmptyState comprehensive', () => {
  it('renders default empty state', () => {
    render(<EmptyState />)
    expect(screen.getByText('NO DATA FOUND')).toBeInTheDocument()
    expect(screen.getByText('There are no items to display.')).toBeInTheDocument()
  })

  it('renders custom title and description', () => {
    render(<EmptyState title="EMPTY" description="No items" />)
    expect(screen.getByText('EMPTY')).toBeInTheDocument()
    expect(screen.getByText('No items')).toBeInTheDocument()
  })

  it('renders action button', () => {
    render(<EmptyState action={<button>CREATE</button>} />)
    expect(screen.getByText('CREATE')).toBeInTheDocument()
  })

  it('renders custom className', () => {
    render(<EmptyState className="custom-class" />)
    const emptyDiv = screen.getByText('NO DATA FOUND').closest('div')
    expect(emptyDiv).toHaveClass('custom-class')
  })
})
