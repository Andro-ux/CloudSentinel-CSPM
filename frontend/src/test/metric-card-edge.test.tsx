import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MetricCard } from '../components/common/MetricCard'

describe('MetricCard edge cases', () => {
  it('renders with zero value', () => {
    render(<MetricCard title="ZERO" value={0} />)
    expect(screen.getByText('ZERO')).toBeInTheDocument()
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('renders without change', () => {
    render(<MetricCard title="NO CHANGE" value={10} />)
    expect(screen.getByText('NO CHANGE')).toBeInTheDocument()
    expect(screen.queryByText('%')).not.toBeInTheDocument()
  })

  it('renders with string value', () => {
    render(<MetricCard title="STRING" value="N/A" />)
    expect(screen.getByText('N/A')).toBeInTheDocument()
  })
})
