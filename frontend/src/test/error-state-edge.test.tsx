import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorState } from '../components/common/ErrorState'

describe('ErrorState edge cases', () => {
  it('renders without retry button', () => {
    render(<ErrorState />)
    expect(screen.queryByText('RETRY')).not.toBeInTheDocument()
  })

  it('renders empty title and message', () => {
    render(<ErrorState title="" message="" />)
    expect(screen.getByText('SYSTEM ERROR')).toBeInTheDocument()
  })

  it('calls onRetry multiple times', () => {
    const handleRetry = vi.fn()
    render(<ErrorState onRetry={handleRetry} />)
    fireEvent.click(screen.getByText('RETRY'))
    fireEvent.click(screen.getByText('RETRY'))
    expect(handleRetry).toHaveBeenCalledTimes(2)
  })
})
