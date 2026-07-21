import { cn } from '../../utils/cn'

interface StatusIndicatorProps {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'loading'
  label?: string
  className?: string
}

const statusConfig = {
  healthy: { color: 'bg-retro-healthy', label: 'ONLINE' },
  degraded: { color: 'bg-retro-medium', label: 'DEGRADED' },
  unhealthy: { color: 'bg-retro-critical', label: 'OFFLINE' },
  loading: { color: 'bg-retro-accent animate-pulse', label: 'LOADING' },
}

export function StatusIndicator({ status, label, className }: StatusIndicatorProps) {
  const config = statusConfig[status]

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className={cn('h-2.5 w-2.5 rounded-full shadow-sm', config.color)} />
      <span className="text-xs font-mono text-retro-text-muted">
        {label || config.label}
      </span>
    </div>
  )
}
