import { cn } from '../../utils/cn'

interface EmptyStateProps {
  title?: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const resolvedTitle = title || 'NO DATA FOUND'
  const resolvedDescription = description || 'There are no items to display.'
  return (
    <div className={cn('flex flex-col items-center justify-center py-12', className)}>
      <div className="text-6xl mb-4 opacity-50">📭</div>
      <h3 className="text-lg font-retro text-retro-text-muted mb-2">{resolvedTitle}</h3>
      <p className="text-sm text-retro-text-muted mb-4 max-w-md text-center">
        {resolvedDescription}
      </p>
      {action}
    </div>
  )
}
