import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { LoginPage } from '../pages/Login'
import { AuthProvider } from '../store/auth'
import { login as mockLogin } from '../api/auth'

vi.mock('../api/auth', () => ({
  login: vi.fn(),
}))

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{ui}</AuthProvider>
    </BrowserRouter>
  )
}

describe('LoginPage', () => {
  it('renders login form', () => {
    renderWithProviders(<LoginPage />)
    expect(screen.getByText('CLOUDSENTINEL')).toBeInTheDocument()
    expect(screen.getByText('LOGIN')).toBeInTheDocument()
  })

  it('shows validation errors for short username', async () => {
    renderWithProviders(<LoginPage />)
    const usernameInput = screen.getByPlaceholderText('Enter username')
    const passwordInput = screen.getByPlaceholderText('Enter password')
    const submitButton = screen.getByText('LOGIN')

    fireEvent.change(usernameInput, { target: { value: 'ab' } })
    fireEvent.change(passwordInput, { target: { value: 'short' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Username must be at least 3 characters')).toBeInTheDocument()
    })
  })

  it('shows validation error for short password', async () => {
    renderWithProviders(<LoginPage />)
    const usernameInput = screen.getByPlaceholderText('Enter username')
    const passwordInput = screen.getByPlaceholderText('Enter password')
    const submitButton = screen.getByText('LOGIN')

    fireEvent.change(usernameInput, { target: { value: 'validuser' } })
    fireEvent.change(passwordInput, { target: { value: 'short' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 12 characters')).toBeInTheDocument()
    })
  })

  it('submits form with valid credentials', async () => {
    vi.mocked(mockLogin).mockResolvedValue({
      success: true,
      data: {
        access_token: 'test-token',
        refresh_token: 'test-refresh',
        token_type: 'bearer',
        expires_in: 3600,
        user: { id: 1, username: 'testuser', organization_id: 1 },
      },
    })

    renderWithProviders(<LoginPage />)
    const usernameInput = screen.getByPlaceholderText('Enter username')
    const passwordInput = screen.getByPlaceholderText('Enter password')
    const submitButton = screen.getByText('LOGIN')

    fireEvent.change(usernameInput, { target: { value: 'validuser' } })
    fireEvent.change(passwordInput, { target: { value: 'validpassword123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('validuser', 'validpassword123')
    })
  })
})
