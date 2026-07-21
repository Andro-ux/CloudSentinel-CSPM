import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SectionHeader } from '../components/common/SectionHeader'

describe('SectionHeader', () => {
  it('renders title', () => {
    render(<SectionHeader title="TEST TITLE" />)
    expect(screen.getByText('TEST TITLE')).toBeInTheDocument()
  })

  it('renders subtitle', () => {
    render(<SectionHeader title="Title" subtitle="Subtitle text" />)
    expect(screen.getByText('Subtitle text')).toBeInTheDocument()
  })

  it('renders action button', () => {
    render(<SectionHeader title="Title" action={<button>Action</button>} />)
    expect(screen.getByText('Action')).toBeInTheDocument()
  })
})
