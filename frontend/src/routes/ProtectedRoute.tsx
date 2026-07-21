import { Navigate } from 'react-router-dom'
import { useAuth } from '../store/auth'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-retro-bg">
        <div className="text-sm font-retro text-retro-primary animate-pulse">
          LOADING...
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
