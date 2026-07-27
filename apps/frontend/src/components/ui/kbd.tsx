import * as React from 'react';
import { cn } from '@/lib/utils';

export interface KbdProps extends React.HTMLAttributes<HTMLElement> {}

const Kbd = React.forwardRef<HTMLElement, KbdProps>(({ className, ...props }, ref) => (
  <kbd
    ref={ref}
    className={cn(
      'inline-flex min-w-5 items-center justify-center rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground shadow-sm',
      className,
    )}
    {...props}
  />
));

Kbd.displayName = 'Kbd';

export { Kbd };
