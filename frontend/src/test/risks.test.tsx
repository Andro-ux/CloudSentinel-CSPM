import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { RisksPage } from '../pages/Risks'
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

describe('RisksPage', () => {
  beforeEach(() => {
    cleanup()
  })

  it('shows loading state initially', () => {
    renderWithProviders(<RisksPage />)
    expect(screen.getByText('LOADING RISKS...')).toBeInTheDocument()
  })

  it('shows error state on failure', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('API Error'))
    renderWithProviders(<RisksPage />)

    await waitFor(() => {
      expect(screen.getByText('RISKS ERROR')).toBeInTheDocument()
    }, { timeout: 3000 })
  })
})
