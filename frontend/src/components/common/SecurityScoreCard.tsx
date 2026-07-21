import { cn } from '../../utils/cn'

interface SecurityScoreCardProps {
  score: number
  grade: string
  label?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function SecurityScoreCard({
  score,
  grade,
  label = 'SECURITY SCORE',
  size = 'md',
  className,
}: SecurityScoreCardProps) {
  const sizeClasses = {
    sm: 'w-24 h-24 text-2xl',
    md: 'w-32 h-32 text-4xl',
    lg: 'w-48 h-48 text-6xl',
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-retro-healthy'
    if (score >= 70) return 'text-retro-low'
    if (score >= 50) return 'text-retro-medium'
    if (score >= 30) return 'text-retro-high'
    return 'text-retro-critical'
  }

  const getGradeColor = (grade: string) => {
    if (grade === 'A') return 'text-retro-healthy'
    if (grade === 'B') return 'text-retro-low'
    if (grade === 'C') return 'text-retro-medium'
    if (grade === 'D') return 'text-retro-high'
    return 'text-retro-critical'
  }

  return (
    <div className={cn('flex flex-col items-center justify-center', className)}>
      <div
        className={cn(
          'relative flex items-center justify-center rounded-full border-4 border-retro-primary bg-retro-surface shadow-retro',
          sizeClasses[size]
        )}
      >
        <div className="absolute inset-0 rounded-full border-2 border-retro-primary/20 animate-pulse-slow" />
        <div className="flex flex-col items-center">
          <span className={cn('font-retro', getScoreColor(score))}>
            {score}
          </span>
          <span className={cn('text-xs font-bold mt-1', getGradeColor(grade))}>
            {grade}
          </span>
        </div>
      </div>
      <span className="mt-2 text-xs font-retro text-retro-text-muted tracking-wider">
        {label}
      </span>
    </div>
  )
}
