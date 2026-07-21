import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider, useAuth } from '../store/auth'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>{children}</AuthProvider>
  </BrowserRouter>
)

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with unauthenticated state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })

  it('restores auth from localStorage', () => {
    const user = { id: 1, username: 'test', role_ids: [] }
    const tokens = { access: 'access-token', refresh: 'refresh-token' }
    localStorage.setItem('cloudsentinel_user', JSON.stringify(user))
    localStorage.setItem('cloudsentinel_tokens', JSON.stringify(tokens))

    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.username).toBe('test')
  })

  it('calls login and updates state', async () => {
    const mockResponse = {
      data: {
        access_token: 'new-access',
        refresh_token: 'new-refresh',
        user: { id: 2, username: 'newuser', organization_id: 1 },
      },
    }
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as any)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await act(async () => {
      await result.current.login('newuser', 'password')
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.username).toBe('newuser')
  })

  it('calls logout and clears state', async () => {
    const user = { id: 1, username: 'test', role_ids: [] }
    const tokens = { access: 'access-token', refresh: 'refresh-token' }
    localStorage.setItem('cloudsentinel_user', JSON.stringify(user))
    localStorage.setItem('cloudsentinel_tokens', JSON.stringify(tokens))

    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as any)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await act(async () => {
      result.current.logout()
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })
})
