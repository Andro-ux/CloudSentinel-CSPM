import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Sidebar } from '../components/layout/Sidebar'
import { AuthProvider } from '../store/auth'

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{ui}</AuthProvider>
    </BrowserRouter>
  )
}

describe('Sidebar comprehensive', () => {
  it('renders all navigation items', () => {
    renderWithProviders(<Sidebar />)
    const navItems = ['Dashboard', 'Assets', 'Findings', 'Risks', 'Graph', 'Providers', 'Settings']
    navItems.forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument()
    })
  })

  it('renders brand name', () => {
    renderWithProviders(<Sidebar />)
    expect(screen.getByText('CLOUDSENTINEL')).toBeInTheDocument()
  })

  it('renders version', () => {
    renderWithProviders(<Sidebar />)
    expect(screen.getByText('v0.12.0')).toBeInTheDocument()
  })

  it('renders logout button', () => {
    renderWithProviders(<Sidebar />)
    expect(screen.getByText('LOGOUT')).toBeInTheDocument()
  })

  it('applies correct styling to brand', () => {
    renderWithProviders(<Sidebar />)
    const brand = screen.getByText('CLOUDSENTINEL')
    expect(brand).toHaveClass('font-retro')
    expect(brand).toHaveClass('tracking-wider')
  })
})
