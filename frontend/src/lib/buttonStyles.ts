import { cn } from './cn';

export type ButtonVariant = 'primary' | 'outline';

/**
 * Fusion21's real CTAs are pill-shaped (border-radius: 100px), in their
 * brand green, used both filled and as an outline. Exposed as a className
 * function (not just a <Button>) because marketing CTAs on HomePage are
 * react-router-dom <Link>s, not <button>s — sharing the classes avoids a
 * polymorphic `as` prop for what's only a couple of call sites.
 */
export function pillButtonClasses(variant: ButtonVariant = 'primary', className?: string): string {
  return cn(
    'inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold',
    'transition-all duration-150 ease-out',
    'hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98]',
    'disabled:pointer-events-none disabled:opacity-50 disabled:hover:translate-y-0',
    variant === 'primary' && 'bg-brand text-white shadow-sm hover:bg-brand-dark hover:shadow-md',
    variant === 'outline' && 'border-2 border-brand text-brand hover:bg-brand-soft hover:shadow-sm',
    className
  );
}
