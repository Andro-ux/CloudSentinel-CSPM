import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MetricCard } from '../components/common/MetricCard'

describe('MetricCard comprehensive', () => {
  it('renders title and value', () => {
    render(<MetricCard title="TEST" value={42} />)
    expect(screen.getByText('TEST')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders increase change', () => {
    render(<MetricCard title="TEST" value={10} change={{ value: 5, type: 'increase' }} />)
    expect(screen.getByText('5%')).toBeInTheDocument()
    expect(screen.getByText('▲')).toBeInTheDocument()
  })

  it('renders decrease change', () => {
    render(<MetricCard title="TEST" value={10} change={{ value: 3, type: 'decrease' }} />)
    expect(screen.getByText('▼')).toBeInTheDocument()
  })

  it('renders neutral change', () => {
    render(<MetricCard title="TEST" value={10} change={{ value: 0, type: 'neutral' }} />)
    expect(screen.getByText('●')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(<MetricCard title="TEST" value={1} icon={<span>📊</span>} />)
    expect(screen.getByText('📊')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<MetricCard title="TEST" value={1} className="custom-class" />)
    const card = document.querySelector('.custom-class')
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('retro-card')
  })
})
