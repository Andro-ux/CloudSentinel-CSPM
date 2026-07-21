import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Sidebar } from '../components/layout/Sidebar'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../store/auth'

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{ui}</AuthProvider>
    </BrowserRouter>
  )
}

describe('Sidebar', () => {
  it('renders navigation items', () => {
    renderWithProviders(<Sidebar />)
    expect(screen.getByText('CLOUDSENTINEL')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Assets')).toBeInTheDocument()
    expect(screen.getByText('Findings')).toBeInTheDocument()
    expect(screen.getByText('Risks')).toBeInTheDocument()
    expect(screen.getByText('Graph')).toBeInTheDocument()
    expect(screen.getByText('Providers')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('renders logout button', () => {
    renderWithProviders(<Sidebar />)
    expect(screen.getByText('LOGOUT')).toBeInTheDocument()
  })

  it('renders version', () => {
    renderWithProviders(<Sidebar />)
    expect(screen.getByText('v0.12.0')).toBeInTheDocument()
  })
})
