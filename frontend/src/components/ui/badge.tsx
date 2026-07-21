import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../utils/cn'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-retro-primary focus:ring-offset-2 focus:ring-offset-retro-bg',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-retro-primary text-retro-bg',
        secondary: 'border-transparent bg-retro-surface-alt text-retro-text',
        destructive: 'border-transparent bg-retro-critical text-white',
        outline: 'text-retro-text border-retro-border',
        critical: 'border-retro-critical text-retro-critical bg-retro-critical/10',
        high: 'border-retro-high text-retro-high bg-retro-high/10',
        medium: 'border-retro-medium text-retro-medium bg-retro-medium/10',
        low: 'border-retro-low text-retro-low bg-retro-low/10',
        healthy: 'border-retro-healthy text-retro-healthy bg-retro-healthy/10',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
