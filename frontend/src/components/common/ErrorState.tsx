import { cn } from '../../utils/cn'

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  title,
  message,
  onRetry,
  className,
}: ErrorStateProps) {
  const resolvedTitle = title || 'SYSTEM ERROR'
  const resolvedMessage = message || 'Something went wrong while loading data.'
  return (
    <div className={cn('flex flex-col items-center justify-center py-12', className)}>
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-lg font-retro text-retro-critical mb-2">{resolvedTitle}</h3>
      <p className="text-sm text-retro-text-muted mb-4 max-w-md text-center">
        {resolvedMessage}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="retro-btn text-sm"
        >
          RETRY
        </button>
      )}
    </div>
  )
}
