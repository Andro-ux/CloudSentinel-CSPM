import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorState } from '../components/common/ErrorState'

describe('ErrorState comprehensive', () => {
  it('renders default error state without retry', () => {
    render(<ErrorState />)
    expect(screen.getByText('SYSTEM ERROR')).toBeInTheDocument()
    expect(screen.getByText('Something went wrong while loading data.')).toBeInTheDocument()
    expect(screen.queryByText('RETRY')).not.toBeInTheDocument()
  })

  it('renders custom title and message', () => {
    render(<ErrorState title="CUSTOM ERROR" message="Custom error message" />)
    expect(screen.getByText('CUSTOM ERROR')).toBeInTheDocument()
    expect(screen.getByText('Custom error message')).toBeInTheDocument()
  })

  it('renders retry button and calls handler', () => {
    const handleRetry = vi.fn()
    render(<ErrorState onRetry={handleRetry} />)
    const retryButton = screen.getByText('RETRY')
    expect(retryButton).toBeInTheDocument()
    fireEvent.click(retryButton)
    expect(handleRetry).toHaveBeenCalledTimes(1)
  })

  it('renders custom className', () => {
    render(<ErrorState className="custom-class" />)
    const errorDiv = screen.getByText('SYSTEM ERROR').closest('div')
    expect(errorDiv).toHaveClass('custom-class')
  })
})
