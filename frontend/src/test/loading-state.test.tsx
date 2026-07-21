import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoadingState } from '../components/common/LoadingState'

describe('LoadingState comprehensive', () => {
  it('renders default loading state', () => {
    render(<LoadingState />)
    expect(screen.getByText('LOADING...')).toBeInTheDocument()
  })

  it('renders custom text', () => {
    render(<LoadingState text="PLEASE WAIT" />)
    expect(screen.getByText('PLEASE WAIT')).toBeInTheDocument()
  })

  it('renders spinner', () => {
    render(<LoadingState />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('renders custom className', () => {
    render(<LoadingState className="custom-class" />)
    const loadingDiv = screen.getByText('LOADING...').closest('div')
    expect(loadingDiv).toHaveClass('custom-class')
  })
})
