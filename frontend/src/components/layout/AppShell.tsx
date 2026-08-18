import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../../lib/cn';

const NAV_LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/negotiate', label: 'Negotiate', end: false },
  { to: '/cases', label: 'Cases', end: false },
  { to: '/analytics', label: 'Analytics', end: false },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-svh bg-page">
      <header className="sticky top-0 z-20 border-b border-hairline bg-surface/85 backdrop-blur-md">
        <PageHeaderRow />
      </header>
      <main className="animate-fade-in-up">{children}</main>
    </div>
  );
}

function Wordmark() {
  return (
    <span className="flex items-center text-lg font-black tracking-tight text-brand">
      FUSION
      <span className="ml-0.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-brand align-middle text-[10px] font-black text-white">
        21
      </span>
    </span>
  );
}

function PageHeaderRow() {
  return (
    <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
      <NavLink to="/" className="flex items-center gap-3 transition-opacity hover:opacity-80">
        <Wordmark />
        <span className="hidden leading-tight sm:block">
          <span className="block text-sm font-semibold text-ink">Dispute Negotiation</span>
          <span className="block text-xs text-ink-muted">Multi-agent procurement simulator</span>
        </span>
      </NavLink>
      <nav className="flex items-center gap-1">
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              cn(
                'rounded-md px-3 py-1.5 text-sm font-medium transition-all duration-150',
                isActive ? 'bg-brand-soft text-brand' : 'text-ink-secondary hover:-translate-y-px hover:bg-page hover:text-ink'
              )
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
