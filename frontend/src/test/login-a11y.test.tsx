import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { LoginPage } from '../pages/Login'
import { AuthProvider } from '../store/auth'

const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{ui}</AuthProvider>
    </BrowserRouter>
  )
}

describe('LoginPage accessibility', () => {
  it('has accessible form labels', () => {
    renderWithRouter(<LoginPage />)
    const usernameLabel = screen.getByText('USERNAME')
    const passwordLabel = screen.getByText('PASSWORD')
    expect(usernameLabel).toBeInTheDocument()
    expect(passwordLabel).toBeInTheDocument()
  })

  it('has accessible form inputs', () => {
    renderWithRouter(<LoginPage />)
    const usernameInput = screen.getByPlaceholderText('Enter username')
    const passwordInput = screen.getByPlaceholderText('Enter password')
    expect(usernameInput).toHaveAttribute('autocomplete', 'username')
    expect(passwordInput).toHaveAttribute('autocomplete', 'current-password')
  })
})
