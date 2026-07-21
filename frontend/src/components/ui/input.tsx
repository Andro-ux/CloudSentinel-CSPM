import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../utils/cn'

const inputVariants = cva(
  'flex w-full rounded-md border bg-retro-surface-alt px-3 py-2 text-sm text-retro-text placeholder:text-retro-text-muted focus:outline-none focus:ring-2 focus:ring-retro-primary/50 disabled:cursor-not-allowed disabled:opacity-50 transition-all',
  {
    variants: {
      variant: {
        default: 'border-retro-border focus:border-retro-primary',
        retro: 'border-2 border-retro-primary/30 bg-retro-bg font-mono text-xs focus:border-retro-primary shadow-retro-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(inputVariants({ variant, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input, inputVariants }
