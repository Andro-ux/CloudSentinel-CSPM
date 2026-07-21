import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../utils/cn'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-retro-primary disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-retro-primary text-retro-bg shadow-retro-sm hover:shadow-retro hover:-translate-y-0.5 active:translate-y-0',
        secondary: 'bg-transparent border-2 border-retro-primary text-retro-primary shadow-retro-sm hover:shadow-retro',
        destructive: 'bg-retro-critical text-white shadow-retro-sm hover:shadow-lg',
        outline: 'border-2 border-retro-border text-retro-text hover:border-retro-primary hover:text-retro-primary',
        ghost: 'hover:bg-retro-surface-alt hover:text-retro-primary',
        retro: 'bg-retro-accent text-retro-bg font-retro text-xs shadow-retro hover:shadow-retro-sm',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
