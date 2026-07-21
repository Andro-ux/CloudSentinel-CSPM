import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SeverityBadge } from '../components/common/SeverityBadge'

describe('SeverityBadge edge cases', () => {
  it('renders unknown severity as info', () => {
    render(<SeverityBadge severity="unknown" />)
    expect(screen.getByText('INFO')).toBeInTheDocument()
  })

  it('renders empty severity as info', () => {
    render(<SeverityBadge severity="" />)
    expect(screen.getByText('INFO')).toBeInTheDocument()
  })

  it('is case insensitive', () => {
    render(<SeverityBadge severity="CRITICAL" />)
    expect(screen.getByText('CRITICAL')).toBeInTheDocument()
  })
})
