import { cn } from '../../utils/cn'

interface SeverityBadgeProps {
  severity: string
  className?: string
}

const severityConfig = {
  critical: { label: 'CRITICAL', color: 'text-retro-critical border-retro-critical bg-retro-critical/10' },
  high: { label: 'HIGH', color: 'text-retro-high border-retro-high bg-retro-high/10' },
  medium: { label: 'MEDIUM', color: 'text-retro-medium border-retro-medium bg-retro-medium/10' },
  low: { label: 'LOW', color: 'text-retro-low border-retro-low bg-retro-low/10' },
  info: { label: 'INFO', color: 'text-retro-text-muted border-retro-border bg-retro-surface-alt' },
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = severityConfig[severity.toLowerCase() as keyof typeof severityConfig] || severityConfig.info

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
