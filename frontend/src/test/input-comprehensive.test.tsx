import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Input } from '../components/ui/input'

describe('Input comprehensive', () => {
  it('renders with placeholder', () => {
    render(<Input placeholder="Enter text" />)
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
  })

  it('renders with value', () => {
    render(<Input value="test" onChange={() => {}} />)
    expect(screen.getByDisplayValue('test')).toBeInTheDocument()
  })

  it('applies default variant', () => {
    render(<Input variant="default" />)
    expect(screen.getByRole('textbox')).toHaveClass('border-retro-border')
  })

  it('applies retro variant', () => {
    render(<Input variant="retro" />)
    expect(screen.getByRole('textbox')).toHaveClass('font-mono')
  })

  it('is disabled when disabled', () => {
    render(<Input disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('handles onChange', () => {
    const handleChange = vi.fn()
    render(<Input onChange={handleChange} />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'new' } })
    expect(handleChange).toHaveBeenCalled()
  })

  it('applies custom className', () => {
    render(<Input className="custom-class" />)
    expect(screen.getByRole('textbox')).toHaveClass('custom-class')
  })
})
