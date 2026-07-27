import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import type { LucideIcon } from 'lucide-react';

const iconButtonVariants = cva(
  'inline-flex items-center justify-center rounded-md p-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        ghost: 'bg-transparent hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        sm: 'h-8 w-8',
        md: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  },
);

export interface IconButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof iconButtonVariants> {
  icon: LucideIcon;
  label: string;
}

const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant, size, icon: Icon, label, type = 'button', ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={iconButtonVariants({ variant, size, className })}
      aria-label={label}
      {...props}
    >
      <Icon className="h-5 w-5" aria-hidden="true" />
    </button>
  ),
);

IconButton.displayName = 'IconButton';

export { IconButton, iconButtonVariants };
