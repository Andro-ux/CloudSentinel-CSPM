export const API_BASE_URL = '/api/v1'
export const APP_VERSION = '0.12.0'
export const APP_NAME = 'CloudSentinel'
export const DEFAULT_PAGE_SIZE = 25
export const TOKEN_REFRESH_INTERVAL = 300000

export const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard' },
  { path: '/assets', label: 'Assets', icon: 'Box' },
  { path: '/findings', label: 'Findings', icon: 'FileSearch' },
  { path: '/risks', label: 'Risks', icon: 'Shield' },
  { path: '/graph', label: 'Graph', icon: 'Network' },
  { path: '/providers', label: 'Providers', icon: 'Server' },
  { path: '/settings', label: 'Settings', icon: 'Settings' },
]

export const SEVERITY_COLORS = {
  critical: 'text-retro-critical border-retro-critical bg-retro-critical/10',
  high: 'text-retro-high border-retro-high bg-retro-high/10',
  medium: 'text-retro-medium border-retro-medium bg-retro-medium/10',
  low: 'text-retro-low border-retro-low bg-retro-low/10',
  info: 'text-retro-text-muted border-retro-border bg-retro-surface-alt',
} as const

export const PRIORITY_COLORS = {
  critical: 'text-retro-critical border-retro-critical bg-retro-critical/10',
  high: 'text-retro-high border-retro-high bg-retro-high/10',
  medium: 'text-retro-medium border-retro-medium bg-retro-medium/10',
  low: 'text-retro-low border-retro-low bg-retro-low/10',
} as const

export const SCORE_COLORS = {
  healthy: 'text-retro-healthy',
  low: 'text-retro-low',
  medium: 'text-retro-medium',
  high: 'text-retro-high',
  critical: 'text-retro-critical',
} as const
