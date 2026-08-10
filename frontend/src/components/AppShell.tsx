'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { href: '/transactions', label: 'TRANSACTIONS' },
  { href: '/assets', label: 'ASSETS' },
  { href: '/reports', label: 'REPORTS' },
  { href: '/recurring-transactions', label: 'RECURRING' },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-bg">
      <div className="grid min-h-screen grid-cols-[168px_1fr] border border-line bg-paper">
        <nav className="bg-nav-bg py-4 font-mono text-base text-nav-ink">
          <div className="mb-2.5 border-b border-white/10 px-4 pb-3.5 tracking-wide text-nav-ink">
            household budget
          </div>
          {NAV_ITEMS.map((item) => {
            const isCurrent = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  isCurrent
                    ? 'block border-l-2 border-accent bg-white/5 px-4 py-2.5 text-nav-ink'
                    : 'block border-l-2 border-transparent px-4 py-2.5 text-nav-ink-dim'
                }
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="overflow-auto p-5">{children}</div>
      </div>
    </div>
  );
}
