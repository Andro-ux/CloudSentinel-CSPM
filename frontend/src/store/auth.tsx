import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { User } from './types'

export interface AuthState {
  user: User | null
  tokens: { access_token: string; refresh_token: string } | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  refreshTokens: () => Promise<void>
  setAuth: (user: User, tokens: { access_token: string; refresh_token: string }) => void
}

export const AuthContext = createContext<AuthContextType | null>(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>(() => {
    const tokens = localStorage.getItem('cloudsentinel_tokens')
    const user = localStorage.getItem('cloudsentinel_user')
    return {
      user: user ? JSON.parse(user) : null,
      tokens: tokens ? JSON.parse(tokens) : null,
      isAuthenticated: !!tokens && !!user,
      isLoading: false,
    }
  })

  const login = async (username: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true }))
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
      })
      if (!response.ok) throw new Error('Login failed')
      const data = await response.json()
      const tokens = {
        access_token: data.data.access_token,
        refresh_token: data.data.refresh_token,
      }
      const user: User = {
        id: data.data.user.id,
        username: data.data.user.username,
        organization_id: data.data.user.organization_id,
        role_ids: [],
      }
      localStorage.setItem('cloudsentinel_tokens', JSON.stringify(tokens))
      localStorage.setItem('cloudsentinel_user', JSON.stringify(user))
      setState({ user, tokens, isAuthenticated: true, isLoading: false })
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }))
      throw error
    }
  }

  const logout = () => {
    const tokens = state.tokens
    if (tokens) {
      fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      }).catch(() => {})
    }
    localStorage.removeItem('cloudsentinel_tokens')
    localStorage.removeItem('cloudsentinel_user')
    setState({ user: null, tokens: null, isAuthenticated: false, isLoading: false })
  }

  const refreshTokens = async () => {
    if (!state.tokens?.refresh_token) return
    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: state.tokens.refresh_token }),
      })
      if (!response.ok) throw new Error('Refresh failed')
      const data = await response.json()
      const tokens = {
        access_token: data.data.access_token,
        refresh_token: data.data.refresh_token,
      }
      localStorage.setItem('cloudsentinel_tokens', JSON.stringify(tokens))
      setState(prev => ({ ...prev, tokens }))
    } catch (error) {
      logout()
    }
  }

  useEffect(() => {
    const interval = setInterval(() => {
      if (state.tokens?.access_token) {
        refreshTokens()
      }
    }, 300000)
    return () => clearInterval(interval)
  }, [state.tokens])

  const setAuth = (user: User, tokens: { access_token: string; refresh_token: string }) => {
    localStorage.setItem('cloudsentinel_tokens', JSON.stringify(tokens))
    localStorage.setItem('cloudsentinel_user', JSON.stringify(user))
    setState({ user, tokens, isAuthenticated: true, isLoading: false })
  }

  return (
    <AuthContext.Provider value={{ ...state, login, logout, refreshTokens, setAuth }}>
      {children}
    </AuthContext.Provider>
  )
}
