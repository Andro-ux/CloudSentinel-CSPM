import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { StatusIndicator } from '../common/StatusIndicator'

export function Layout() {
  return (
    <div className="flex h-screen bg-retro-bg">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-retro-border bg-retro-surface px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-retro text-retro-text tracking-wider">
          SECURITY CONSOLE
        </h2>
      </div>
      <div className="flex items-center gap-4">
        <StatusIndicator status="healthy" />
      </div>
    </header>
  )
}
