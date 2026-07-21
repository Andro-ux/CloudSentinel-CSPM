import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { DashboardPage } from '../pages/Dashboard'
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

describe('DashboardPage', () => {
  beforeEach(() => {
    cleanup()
  })

  it('shows loading state initially', () => {
    renderWithProviders(<DashboardPage />)
    expect(screen.getByText('LOADING DASHBOARD...')).toBeInTheDocument()
  })

  it('shows error state on failure', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('API Error'))
    renderWithProviders(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('DASHBOARD ERROR')).toBeInTheDocument()
    }, { timeout: 3000 })
  })
})
