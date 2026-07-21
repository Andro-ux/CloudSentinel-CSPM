import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { SettingsPage } from '../pages/Settings'
import { AuthProvider } from '../store/auth'

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{ui}</AuthProvider>
    </BrowserRouter>
  )
}

describe('SettingsPage', () => {
  it('renders settings page', () => {
    renderWithProviders(<SettingsPage />)
    expect(screen.getByText('SETTINGS')).toBeInTheDocument()
    expect(screen.getByText('PREFERENCES')).toBeInTheDocument()
    expect(screen.getByText('API KEYS')).toBeInTheDocument()
  })
})
