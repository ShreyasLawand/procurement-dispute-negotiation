import { AlertOctagon } from 'lucide-react';
import { z } from 'zod';
import { cn } from '../../lib/cn';

function issuesFromZodError(err: z.ZodError): string[] {
  return err.issues.map((issue) => {
    const path = issue.path.join('.');
    return path ? `${path}: ${issue.message}` : issue.message;
  });
}

/** Flattens a raw error into human-readable lines. Understands the
 * AggregateError of two ZodErrors thrown by parseUnknownDoc() and renders
 * real per-field validation issues instead of a generic message. */
export function formatError(error: unknown): string[] {
  if (error instanceof AggregateError) {
    return error.errors.flatMap((e, i) => {
      if (e instanceof z.ZodError) {
        const label = i === 0 ? 'As a negotiation case:' : 'As a batch summary:';
        return [label, ...issuesFromZodError(e).map((line) => `  ${line}`)];
      }
      return [String(e)];
    });
  }
  if (error instanceof z.ZodError) {
    return issuesFromZodError(error);
  }
  if (error instanceof Error) {
    return [error.message];
  }
  return [String(error)];
}

interface ErrorStateProps {
  title?: string;
  error: unknown;
  className?: string;
}

export function ErrorState({ title = 'Something went wrong', error, className }: ErrorStateProps) {
  const lines = formatError(error);
  return (
    <div className={cn('rounded-xl border border-critical/20 bg-critical-soft px-5 py-4', className)}>
      <div className="flex items-start gap-2.5">
        <AlertOctagon className="mt-0.5 h-4 w-4 shrink-0 text-critical" />
        <div className="min-w-0">
          <p className="font-medium text-critical">{title}</p>
          <ul className="mt-1.5 space-y-0.5 text-sm text-ink-secondary">
            {lines.map((line, i) => (
              <li key={i} className="break-words font-mono text-xs">
                {line}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
