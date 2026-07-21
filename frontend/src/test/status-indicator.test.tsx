import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusIndicator } from '../components/common/StatusIndicator'

describe('StatusIndicator comprehensive', () => {
  it('renders all statuses', () => {
    const statuses = [
      { status: 'healthy' as const, label: 'ONLINE' },
      { status: 'degraded' as const, label: 'DEGRADED' },
      { status: 'unhealthy' as const, label: 'OFFLINE' },
      { status: 'loading' as const, label: 'LOADING' },
    ]
    statuses.forEach(({ status, label }) => {
      render(<StatusIndicator status={status} />)
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })

  it('renders with custom label', () => {
    render(<StatusIndicator status="healthy" label="CUSTOM" />)
    expect(screen.getByText('CUSTOM')).toBeInTheDocument()
  })

  it('renders indicator dot', () => {
    render(<StatusIndicator status="healthy" />)
    const dot = document.querySelector('.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<StatusIndicator status="healthy" label="ONLINE" className="custom-class" />)
    const indicator = screen.getByText('ONLINE').closest('div')
    expect(indicator).toHaveClass('custom-class')
  })
})
