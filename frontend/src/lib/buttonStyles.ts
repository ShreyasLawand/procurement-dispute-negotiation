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
    'inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold transition-colors',
    variant === 'primary' && 'bg-brand text-white hover:bg-brand-dark',
    variant === 'outline' && 'border-2 border-brand text-brand hover:bg-brand-soft',
    className
  );
}
