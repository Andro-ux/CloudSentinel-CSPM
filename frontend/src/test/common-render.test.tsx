import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RiskBadge } from '../components/common/RiskBadge'
import { SeverityBadge } from '../components/common/SeverityBadge'
import { StatusIndicator } from '../components/common/StatusIndicator'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { EmptyState } from '../components/common/EmptyState'
import { MetricCard } from '../components/common/MetricCard'
import { SectionHeader } from '../components/common/SectionHeader'

describe('Common components rendering', () => {
  it('renders RiskBadge for all priorities', () => {
    const priorities = ['critical', 'high', 'medium', 'low'] as const
    priorities.forEach(priority => {
      render(<RiskBadge priority={priority} />)
      expect(screen.getByText(priority.toUpperCase())).toBeInTheDocument()
    })
  })

  it('renders SeverityBadge for all severities', () => {
    const severities = ['critical', 'high', 'medium', 'low', 'info'] as const
    severities.forEach(severity => {
      render(<SeverityBadge severity={severity} />)
      expect(screen.getByText(severity.toUpperCase())).toBeInTheDocument()
    })
  })

  it('renders StatusIndicator for all statuses', () => {
    const statuses = [
      { status: 'healthy', label: 'ONLINE' },
      { status: 'degraded', label: 'DEGRADED' },
      { status: 'unhealthy', label: 'OFFLINE' },
      { status: 'loading', label: 'LOADING' },
    ] as const
    statuses.forEach(({ status, label }) => {
      render(<StatusIndicator status={status} />)
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })

  it('renders LoadingState with custom text', () => {
    render(<LoadingState text="CUSTOM LOADING" />)
    expect(screen.getByText('CUSTOM LOADING')).toBeInTheDocument()
  })

  it('renders ErrorState without retry', () => {
    render(<ErrorState />)
    expect(screen.queryByText('RETRY')).not.toBeInTheDocument()
  })

  it('renders EmptyState with action', () => {
    render(<EmptyState action={<button>CREATE</button>} />)
    expect(screen.getByText('CREATE')).toBeInTheDocument()
  })

  it('renders MetricCard with all props', () => {
    render(
      <MetricCard
        title="TEST"
        value="100"
        change={{ value: 10, type: 'increase' }}
        icon={<span>📊</span>}
      />
    )
    expect(screen.getByText('TEST')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('10%')).toBeInTheDocument()
  })

  it('renders SectionHeader with all props', () => {
    render(<SectionHeader title="TITLE" subtitle="SUBTITLE" action={<button>ACTION</button>} />)
    expect(screen.getByText('TITLE')).toBeInTheDocument()
    expect(screen.getByText('SUBTITLE')).toBeInTheDocument()
    expect(screen.getByText('ACTION')).toBeInTheDocument()
  })
})
