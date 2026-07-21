import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { ThemeProvider, useTheme } from '../store/theme'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
)

describe('ThemeProvider', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark', 'light')
  })

  it('defaults to dark theme', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })
    expect(result.current.theme).toBe('dark')
    expect(result.current.resolvedTheme).toBe('dark')
  })

  it('allows changing theme', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })
    act(() => {
      result.current.setTheme('light')
    })
    expect(result.current.theme).toBe('light')
    expect(result.current.resolvedTheme).toBe('light')
  })

  it('persists theme to localStorage', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })
    act(() => {
      result.current.setTheme('system')
    })
    expect(localStorage.getItem('theme')).toBe('system')
  })
})
