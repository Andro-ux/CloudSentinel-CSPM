import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { LoginPage } from '../pages/Login'
import { AuthProvider } from '../store/auth'

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
}

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>{ui}</AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('LoginPage comprehensive', () => {
  beforeEach(() => {
    cleanup()
  })

  it('renders all form elements', () => {
    renderWithProviders(<LoginPage />)
    expect(screen.getByText('USERNAME')).toBeInTheDocument()
    expect(screen.getByText('PASSWORD')).toBeInTheDocument()
    expect(screen.getByText('LOGIN')).toBeInTheDocument()
    expect(screen.getByText('AUTHORIZED ACCESS ONLY')).toBeInTheDocument()
  })

  it('shows error on invalid credentials', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('Invalid'))
    renderWithProviders(<LoginPage />)

    fireEvent.change(screen.getByPlaceholderText('Enter username'), { target: { value: 'user' } })
    fireEvent.change(screen.getByPlaceholderText('Enter password'), { target: { value: 'passwordlong123' } })
    fireEvent.click(screen.getByText('LOGIN'))

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials. Please try again.')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('clears error when form is updated', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('Invalid'))
    renderWithProviders(<LoginPage />)

    fireEvent.change(screen.getByPlaceholderText('Enter username'), { target: { value: 'user' } })
    fireEvent.change(screen.getByPlaceholderText('Enter password'), { target: { value: 'passwordlong123' } })
    fireEvent.click(screen.getByText('LOGIN'))

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials. Please try again.')).toBeInTheDocument()
    }, { timeout: 3000 })

    fireEvent.change(screen.getByPlaceholderText('Enter username'), { target: { value: 'newuser' } })
    expect(screen.queryByText('Invalid credentials. Please try again.')).not.toBeInTheDocument()
  })
})
