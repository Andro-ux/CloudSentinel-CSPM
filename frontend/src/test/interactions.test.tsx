import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card } from '../components/ui/card'
import { Badge } from '../components/ui/badge'

describe('UI component interactions', () => {
  it('Button responds to clicks', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('Input responds to typing', () => {
    const handleChange = vi.fn()
    render(<Input onChange={handleChange} />)
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'hello' } })
    expect(handleChange).toHaveBeenCalled()
  })

  it('Card can be clicked', () => {
    const handleClick = vi.fn()
    render(<Card onClick={handleClick}>Clickable card</Card>)
    fireEvent.click(screen.getByText('Clickable card'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('Badge can be clicked', () => {
    const handleClick = vi.fn()
    render(<Badge onClick={handleClick}>Clickable badge</Badge>)
    fireEvent.click(screen.getByText('Clickable badge'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
