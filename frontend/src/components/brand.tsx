import Link from "next/link";

import { cn } from "@/lib/cn";

export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={cn("size-8", className)} aria-hidden>
      <rect width="32" height="32" rx="9" fill="var(--brand)" />
      <path
        d="M6.5 17.5h4.2l2.4-6 3.6 11 2.8-8 1.7 3h4.3"
        fill="none"
        stroke="var(--brand-ink)"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Logo({ href = "/", className }: { href?: string; className?: string }) {
  return (
    <Link href={href} className={cn("inline-flex items-center gap-2.5 font-semibold tracking-tight text-ink", className)}>
      <LogoMark />
      <span className="text-[17px]">NeuroTrack</span>
    </Link>
  );
}
