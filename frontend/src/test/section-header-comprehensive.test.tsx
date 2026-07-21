import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SectionHeader } from '../components/common/SectionHeader'

describe('SectionHeader comprehensive', () => {
  it('renders title only', () => {
    render(<SectionHeader title="ONLY TITLE" />)
    expect(screen.getByText('ONLY TITLE')).toBeInTheDocument()
  })

  it('renders title and subtitle', () => {
    render(<SectionHeader title="TITLE" subtitle="SUBTITLE" />)
    expect(screen.getByText('TITLE')).toBeInTheDocument()
    expect(screen.getByText('SUBTITLE')).toBeInTheDocument()
  })

  it('renders title with action', () => {
    render(<SectionHeader title="TITLE" action={<button>ACTION</button>} />)
    expect(screen.getByText('TITLE')).toBeInTheDocument()
    expect(screen.getByText('ACTION')).toBeInTheDocument()
  })

  it('renders with custom className', () => {
    render(<SectionHeader title="TITLE" className="custom-class" />)
    const header = document.querySelector('.custom-class')
    expect(header).toBeInTheDocument()
    expect(header).toHaveClass('flex')
  })

  it('applies title and subtitle classes', () => {
    render(<SectionHeader title="TITLE" subtitle="SUBTITLE" />)
    const title = screen.getByText('TITLE')
    expect(title).toHaveClass('font-retro')
    expect(screen.getByText('SUBTITLE')).toHaveClass('text-retro-text-muted')
  })
})
