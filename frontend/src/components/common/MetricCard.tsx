import { cn } from '../../utils/cn'

interface MetricCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    type: 'increase' | 'decrease' | 'neutral'
  }
  icon?: React.ReactNode
  className?: string
}

export function MetricCard({ title, value, change, icon, className }: MetricCardProps) {
  const getChangeColor = (type: string) => {
    if (type === 'increase') return 'text-retro-healthy'
    if (type === 'decrease') return 'text-retro-critical'
    return 'text-retro-text-muted'
  }

  const getChangeIcon = (type: string) => {
    if (type === 'increase') return '▲'
    if (type === 'decrease') return '▼'
    return '●'
  }

  return (
    <div
      className={cn(
        'retro-card p-4 flex flex-col space-y-2',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-retro text-retro-text-muted tracking-wider">
          {title}
        </span>
        {icon && <div className="text-retro-primary">{icon}</div>}
      </div>
      <div className="flex items-end justify-between">
        <span className="text-2xl font-bold text-retro-text font-mono">
          {value}
        </span>
        {change && (
          <span
            className={cn(
              'text-xs font-mono flex items-center gap-1',
              getChangeColor(change.type)
            )}
          >
            <span>{getChangeIcon(change.type)}</span>
            {Math.abs(change.value)}%
          </span>
        )}
      </div>
    </div>
  )
}
