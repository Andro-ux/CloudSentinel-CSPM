import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SectionHeader } from '../components/common/SectionHeader'

describe('SectionHeader accessibility', () => {
  it('renders heading element', () => {
    render(<SectionHeader title="ACCESSIBLE TITLE" />)
    const heading = screen.getByRole('heading', { level: 2 })
    expect(heading).toBeInTheDocument()
    expect(heading).toHaveTextContent('ACCESSIBLE TITLE')
  })
})
