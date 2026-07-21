import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Layout } from '../components/layout/Layout'
import { AuthProvider } from '../store/auth'

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{ui}</AuthProvider>
    </BrowserRouter>
  )
}

describe('Layout comprehensive', () => {
  it('renders layout', () => {
    renderWithProviders(<Layout />)
    expect(screen.getByText('CLOUDSENTINEL')).toBeInTheDocument()
  })

  it('renders sidebar', () => {
    renderWithProviders(<Layout />)
    expect(screen.getByText('CLOUDSENTINEL')).toBeInTheDocument()
  })

  it('renders header', () => {
    renderWithProviders(<Layout />)
    expect(screen.getByText('SECURITY CONSOLE')).toBeInTheDocument()
  })

  it('renders status indicator', () => {
    renderWithProviders(<Layout />)
    expect(screen.getByText('ONLINE')).toBeInTheDocument()
  })
})
