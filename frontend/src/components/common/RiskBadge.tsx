import { cn } from '../../utils/cn'

interface RiskBadgeProps {
  priority: string
  className?: string
}

const priorityConfig = {
  critical: { label: 'CRITICAL', color: 'text-retro-critical border-retro-critical bg-retro-critical/10' },
  high: { label: 'HIGH', color: 'text-retro-high border-retro-high bg-retro-high/10' },
  medium: { label: 'MEDIUM', color: 'text-retro-medium border-retro-medium bg-retro-medium/10' },
  low: { label: 'LOW', color: 'text-retro-low border-retro-low bg-retro-low/10' },
}

export function RiskBadge({ priority, className }: RiskBadgeProps) {
  const config = priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig.low

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold font-retro tracking-wider',
        config.color,
        className
      )}
    >
      {config.label}
    </span>
  )
}
