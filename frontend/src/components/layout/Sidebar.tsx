import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Box,
  FileSearch,
  Shield,
  Network,
  Server,
  Settings,
  LogOut,
} from 'lucide-react'
import { useAuth } from '../../store/auth'
import { cn } from '../../utils/cn'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/assets', icon: Box, label: 'Assets' },
  { to: '/findings', icon: FileSearch, label: 'Findings' },
  { to: '/risks', icon: Shield, label: 'Risks' },
  { to: '/graph', icon: Network, label: 'Graph' },
  { to: '/providers', icon: Server, label: 'Providers' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-retro-border bg-retro-surface">
      <div className="flex h-16 items-center border-b border-retro-border px-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded bg-retro-primary flex items-center justify-center">
            <span className="font-retro text-xs text-retro-bg">CS</span>
          </div>
          <div>
            <h1 className="text-sm font-retro text-retro-text tracking-wider">
              CLOUDSENTINEL
            </h1>
            <p className="text-[10px] text-retro-text-muted font-mono">v0.12.0</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all',
                isActive
                  ? 'bg-retro-primary/10 text-retro-primary shadow-retro-sm'
                  : 'text-retro-text-muted hover:bg-retro-surface-alt hover:text-retro-text'
              )
            }
          >
            <item.icon className="h-4 w-4" />
            <span className="font-mono text-xs tracking-wider">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-retro-border p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-retro-text-muted hover:bg-retro-critical/10 hover:text-retro-critical transition-all"
        >
          <LogOut className="h-4 w-4" />
          <span className="font-mono text-xs tracking-wider">LOGOUT</span>
        </button>
      </div>
    </aside>
  )
}
