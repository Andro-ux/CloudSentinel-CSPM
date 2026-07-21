import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { SecurityScoreCard } from '../components/common/SecurityScoreCard'
import { MetricCard } from '../components/common/MetricCard'
import { RiskBadge } from '../components/common/RiskBadge'
import { SeverityBadge } from '../components/common/SeverityBadge'
import { StatusIndicator } from '../components/common/StatusIndicator'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { EmptyState } from '../components/common/EmptyState'

describe('SecurityScoreCard', () => {
  it('renders score and grade', () => {
    render(<SecurityScoreCard score={85} grade="A" />)
    expect(screen.getByText('85')).toBeInTheDocument()
    expect(screen.getByText('A')).toBeInTheDocument()
  })

  it('applies correct color for high score', () => {
    render(<SecurityScoreCard score={95} grade="A" />)
    const scoreElement = screen.getByText('95')
    expect(scoreElement).toHaveClass('text-retro-healthy')
  })

  it('renders different sizes', () => {
    render(<SecurityScoreCard score={50} grade="C" size="sm" />)
    expect(screen.getByText('SECURITY SCORE')).toBeInTheDocument()
  })
})

describe('MetricCard', () => {
  it('renders title and value', () => {
    render(<MetricCard title="ASSETS" value={42} />)
    expect(screen.getByText('ASSETS')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('shows change indicator', () => {
    render(
      <MetricCard
        title="RISKS"
        value={10}
        change={{ value: 5, type: 'increase' }}
      />
    )
    expect(screen.getByText('5%')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(<MetricCard title="TEST" value={1} icon={<span>🔒</span>} />)
    expect(screen.getByText('🔒')).toBeInTheDocument()
  })
})

describe('RiskBadge', () => {
  it('renders critical priority', () => {
    render(<RiskBadge priority="critical" />)
    expect(screen.getByText('CRITICAL')).toBeInTheDocument()
  })

  it('renders high priority', () => {
    render(<RiskBadge priority="high" />)
    expect(screen.getByText('HIGH')).toBeInTheDocument()
  })

  it('renders medium priority', () => {
    render(<RiskBadge priority="medium" />)
    expect(screen.getByText('MEDIUM')).toBeInTheDocument()
  })

  it('renders low priority', () => {
    render(<RiskBadge priority="low" />)
    expect(screen.getByText('LOW')).toBeInTheDocument()
  })
})

describe('SeverityBadge', () => {
  it('renders critical severity', () => {
    render(<SeverityBadge severity="critical" />)
    expect(screen.getByText('CRITICAL')).toBeInTheDocument()
  })

  it('renders info severity', () => {
    render(<SeverityBadge severity="info" />)
    expect(screen.getByText('INFO')).toBeInTheDocument()
  })

  it('handles unknown severity', () => {
    render(<SeverityBadge severity="unknown" />)
    expect(screen.getByText('INFO')).toBeInTheDocument()
  })
})

describe('StatusIndicator', () => {
  it('renders healthy status', () => {
    render(<StatusIndicator status="healthy" />)
    expect(screen.getByText('ONLINE')).toBeInTheDocument()
  })

  it('renders custom label', () => {
    render(<StatusIndicator status="loading" label="PLEASE WAIT" />)
    expect(screen.getByText('PLEASE WAIT')).toBeInTheDocument()
  })
})

describe('LoadingState', () => {
  it('renders loading text', () => {
    render(<LoadingState />)
    expect(screen.getByText('LOADING...')).toBeInTheDocument()
  })

  it('renders custom text', () => {
    render(<LoadingState text="PLEASE WAIT" />)
    expect(screen.getByText('PLEASE WAIT')).toBeInTheDocument()
  })
})

describe('ErrorState', () => {
  it('renders default error state', () => {
    render(<ErrorState />)
    expect(screen.getByText('SYSTEM ERROR')).toBeInTheDocument()
  })

  it('renders custom message', () => {
    render(<ErrorState title="FAIL" message="Something broke" />)
    expect(screen.getByText('FAIL')).toBeInTheDocument()
    expect(screen.getByText('Something broke')).toBeInTheDocument()
  })

  it('renders retry button when provided', () => {
    const retry = vi.fn()
    render(<ErrorState onRetry={retry} />)
    expect(screen.getByText('RETRY')).toBeInTheDocument()
    fireEvent.click(screen.getByText('RETRY'))
    expect(retry).toHaveBeenCalled()
  })
})

describe('EmptyState', () => {
  it('renders default empty state', () => {
    render(<EmptyState />)
    expect(screen.getByText('NO DATA FOUND')).toBeInTheDocument()
  })

  it('renders custom content', () => {
    render(<EmptyState title="EMPTY" description="Nothing here" />)
    expect(screen.getByText('EMPTY')).toBeInTheDocument()
    expect(screen.getByText('Nothing here')).toBeInTheDocument()
  })
})
