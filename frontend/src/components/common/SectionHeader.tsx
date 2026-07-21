import { cn } from '../../utils/cn'

interface SectionHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
  className?: string
}

export function SectionHeader({ title, subtitle, action, className }: SectionHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between mb-6', className)}>
      <div>
        <h2 className="text-xl font-retro text-retro-text tracking-wide">
          {title}
        </h2>
        {subtitle && (
          <p className="mt-1 text-sm text-retro-text-muted">{subtitle}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
