import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RiskBadge } from '../components/common/RiskBadge'

describe('RiskBadge edge cases', () => {
  it('renders unknown priority as low', () => {
    render(<RiskBadge priority="unknown" />)
    expect(screen.getByText('LOW')).toBeInTheDocument()
  })

  it('renders empty priority as low', () => {
    render(<RiskBadge priority="" />)
    expect(screen.getByText('LOW')).toBeInTheDocument()
  })
})
