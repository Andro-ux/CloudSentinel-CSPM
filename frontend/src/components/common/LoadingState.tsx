import { cn } from '../../utils/cn'

interface LoadingStateProps {
  text?: string
  className?: string
}

export function LoadingState({ text = 'LOADING...', className }: LoadingStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12', className)}>
      <div className="relative w-16 h-16 mb-4">
        <div className="absolute inset-0 border-4 border-retro-primary/20 rounded-full" />
        <div className="absolute inset-0 border-4 border-retro-primary border-t-transparent rounded-full animate-spin" />
      </div>
      <p className="text-sm font-retro text-retro-primary animate-pulse">
        {text}
      </p>
    </div>
  )
}
