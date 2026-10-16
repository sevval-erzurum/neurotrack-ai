"use client";

import { AlertTriangle, CheckCircle2, Info, Loader2, OctagonAlert, X } from "lucide-react";
import Link from "next/link";
import {
  forwardRef,
  useEffect,
  useId,
  useRef,
  type ButtonHTMLAttributes,
  type ComponentProps,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from "react";

import { cn } from "@/lib/cn";
import { RISK_LABEL, initials } from "@/lib/format";
import type { Alert, RiskLevel } from "@/lib/types";

// --- Buton -------------------------------------------------------------------

const buttonStyles = {
  base: "inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 whitespace-nowrap select-none",
  variant: {
    primary: "bg-primary text-primary-ink hover:opacity-90",
    brand: "bg-brand text-brand-ink hover:opacity-90",
    secondary: "bg-surface text-ink border border-line-strong hover:bg-surface-2",
    ghost: "text-ink-2 hover:bg-surface-2 hover:text-ink",
    danger: "bg-critical text-white hover:opacity-90",
  },
  size: { sm: "h-8 px-3", md: "h-10 px-4", lg: "h-12 px-6 text-base", icon: "h-9 w-9" },
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: keyof typeof buttonStyles.variant;
  size?: keyof typeof buttonStyles.size;
  loading?: boolean;
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", size = "md", loading, className, children, disabled, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cn(buttonStyles.base, buttonStyles.variant[variant], buttonStyles.size[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="size-4 animate-spin" aria-hidden />}
      {children}
    </button>
  );
});

export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  ...props
}: ComponentProps<typeof Link> & { variant?: keyof typeof buttonStyles.variant; size?: keyof typeof buttonStyles.size }) {
  return (
    <Link className={cn(buttonStyles.base, buttonStyles.variant[variant], buttonStyles.size[size], className)} {...props} />
  );
}

// --- Kart ----------------------------------------------------------------------

export function Card({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("rounded-card border border-line bg-surface shadow-card", className)} {...props} />;
}

export function CardHeader({
  title,
  description,
  action,
  className,
}: {
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex items-start justify-between gap-4 px-5 pt-5", className)}>
      <div className="min-w-0">
        <h2 className="text-[15px] font-semibold tracking-tight text-ink">{title}</h2>
        {description && <p className="mt-0.5 text-sm text-muted">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

// --- Form ----------------------------------------------------------------------

const fieldBase =
  "w-full rounded-xl border border-line-strong bg-surface px-3 text-sm text-ink placeholder:text-muted transition-colors focus:border-focus focus:outline-none focus:ring-2 focus:ring-focus/20 disabled:opacity-60";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(function Input(
  { className, ...props },
  ref,
) {
  return <input ref={ref} className={cn(fieldBase, "h-10", className)} {...props} />;
});

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(function Textarea(
  { className, ...props },
  ref,
) {
  return <textarea ref={ref} className={cn(fieldBase, "min-h-24 py-2.5 leading-relaxed", className)} {...props} />;
});

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cn(fieldBase, "h-10 pr-8", className)} {...props} />;
}

export function Field({
  label,
  hint,
  error,
  children,
  className,
}: {
  label: string;
  hint?: ReactNode;
  error?: string | null;
  children: (id: string) => ReactNode;
  className?: string;
}) {
  const id = useId();
  return (
    <div className={cn("space-y-1.5", className)}>
      <label htmlFor={id} className="block text-sm font-medium text-ink">
        {label}
      </label>
      {children(id)}
      {error ? (
        <p className="text-xs text-critical-ink" role="alert">
          {error}
        </p>
      ) : hint ? (
        <p className="text-xs text-muted">{hint}</p>
      ) : null}
    </div>
  );
}

export function Scale({
  label,
  value,
  onChange,
  min = 0,
  max = 10,
  step = 1,
  unit,
  lowLabel,
  highLabel,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  lowLabel?: string;
  highLabel?: string;
}) {
  const id = useId();
  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <label htmlFor={id} className="text-sm font-medium text-ink">
          {label}
        </label>
        <span className="tabular text-sm font-semibold text-ink">
          {value}
          {unit && <span className="ml-0.5 font-normal text-muted">{unit}</span>}
        </span>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-[var(--brand)]"
      />
      {(lowLabel || highLabel) && (
        <div className="flex justify-between text-xs text-muted">
          <span>{lowLabel}</span>
          <span>{highLabel}</span>
        </div>
      )}
    </div>
  );
}

// --- Geri bildirim ---------------------------------------------------------------

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-lg bg-surface-2", className)} aria-hidden />;
}

export function Spinner({ label = "Yükleniyor" }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-sm text-muted" role="status">
      <Loader2 className="size-4 animate-spin" aria-hidden />
      {label}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: {
  icon: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center px-6 py-12 text-center", className)}>
      <div className="mb-3 grid size-11 place-items-center rounded-2xl bg-surface-2 text-ink-2">{icon}</div>
      <p className="font-medium text-ink">{title}</p>
      {description && <p className="mt-1 max-w-sm text-sm text-muted">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({ error, retry }: { error: unknown; retry?: () => void }) {
  return (
    <EmptyState
      icon={<AlertTriangle className="size-5" />}
      title="Veriler yüklenemedi"
      description={error instanceof Error ? error.message : undefined}
      action={
        retry && (
          <Button variant="secondary" size="sm" onClick={retry}>
            Tekrar dene
          </Button>
        )
      }
    />
  );
}

// --- Rozetler -----------------------------------------------------------------

const badgeTone = {
  neutral: "bg-surface-2 text-ink-2",
  brand: "bg-brand-soft text-brand",
  good: "bg-good-soft text-good-ink",
  warning: "bg-warning-soft text-warning-ink",
  critical: "bg-critical-soft text-critical-ink",
  info: "bg-info-soft text-info-ink",
};

export function Badge({
  tone = "neutral",
  className,
  ...props
}: ComponentProps<"span"> & { tone?: keyof typeof badgeTone }) {
  return (
    <span
      className={cn("inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium", badgeTone[tone], className)}
      {...props}
    />
  );
}

const RISK_STYLE: Record<RiskLevel, { tone: keyof typeof badgeTone; icon: typeof Info }> = {
  low: { tone: "good", icon: CheckCircle2 },
  elevated: { tone: "warning", icon: AlertTriangle },
  high: { tone: "critical", icon: OctagonAlert },
};

/** Durum rengi hiçbir zaman tek başına anlam taşımaz: ikon + metin birlikte. */
export function RiskBadge({ level, className }: { level: RiskLevel; className?: string }) {
  const { tone, icon: Icon } = RISK_STYLE[level];
  return (
    <Badge tone={tone} className={className}>
      <Icon className="size-3.5" aria-hidden />
      {RISK_LABEL[level]}
    </Badge>
  );
}

const ALERT_STYLE = {
  critical: { className: "bg-critical-soft text-critical-ink", icon: OctagonAlert, label: "Acil" },
  warning: { className: "bg-warning-soft text-warning-ink", icon: AlertTriangle, label: "Dikkat" },
  info: { className: "bg-info-soft text-info-ink", icon: Info, label: "Bilgi" },
};

export function AlertList({ alerts }: { alerts: Alert[] }) {
  if (!alerts.length) {
    return (
      <div className="flex items-center gap-2.5 rounded-xl bg-good-soft px-3.5 py-3 text-sm text-good-ink">
        <CheckCircle2 className="size-4 shrink-0" aria-hidden />
        Şu an dikkat gerektiren bir durum görünmüyor.
      </div>
    );
  }
  return (
    <ul className="space-y-2">
      {alerts.map((alert) => {
        const style = ALERT_STYLE[alert.level];
        return (
          <li key={alert.code} className={cn("flex gap-2.5 rounded-xl px-3.5 py-3 text-sm", style.className)}>
            <style.icon className="mt-0.5 size-4 shrink-0" aria-hidden />
            <span>
              <span className="sr-only">{style.label}: </span>
              {alert.message}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

export function Avatar({ name, className }: { name: string; className?: string }) {
  return (
    <span
      className={cn(
        "grid size-9 shrink-0 place-items-center rounded-full bg-brand-soft text-xs font-semibold text-brand",
        className,
      )}
      aria-hidden
    >
      {initials(name)}
    </span>
  );
}

// --- Diyalog -------------------------------------------------------------------

export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  className,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      onClose={onClose}
      onClick={(e) => e.target === ref.current && onClose()}
      className={cn(
        "m-auto w-[calc(100%-2rem)] max-w-lg rounded-2xl border border-line bg-surface p-0 text-ink shadow-2xl backdrop:bg-black/40 backdrop:backdrop-blur-[2px]",
        className,
      )}
    >
      {open && (
        <div className="max-h-[85vh] overflow-y-auto p-6">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <h2 id={titleId} className="text-lg font-semibold tracking-tight">
                {title}
              </h2>
              {description && <p className="mt-1 text-sm text-muted">{description}</p>}
            </div>
            <Button variant="ghost" size="icon" onClick={onClose} aria-label="Kapat" className="-mr-2 -mt-1">
              <X className="size-4" />
            </Button>
          </div>
          {children}
        </div>
      )}
    </dialog>
  );
}

export function PageHeader({
  title,
  description,
  action,
  eyebrow,
}: {
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  eyebrow?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        {eyebrow && <div className="mb-1.5 text-sm text-muted">{eyebrow}</div>}
        <h1 className="text-2xl font-semibold tracking-tight text-ink sm:text-[28px]">{title}</h1>
        {description && <p className="mt-1 text-[15px] text-ink-2">{description}</p>}
      </div>
      {action && <div className="flex shrink-0 flex-wrap gap-2">{action}</div>}
    </div>
  );
}
