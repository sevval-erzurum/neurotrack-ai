"use client";

import {
  Bell,
  BrainCircuit,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Sparkles,
  X,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useState, type ReactNode } from "react";

import { cn } from "@/lib/cn";
import { ROLE_LABEL } from "@/lib/format";
import { useConversations, useLogout, useMe, useNotifications, useSubjects } from "@/lib/queries";

import { Logo } from "./brand";
import { ThemeToggle } from "./theme-toggle";
import { Avatar, Button, Skeleton, Spinner } from "./ui";

function NavItem({
  href,
  icon: Icon,
  label,
  count,
  active,
}: {
  href: string;
  icon: LucideIcon;
  label: string;
  count?: number;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex h-9 items-center gap-3 rounded-lg px-2.5 text-sm transition-colors",
        active ? "bg-surface-2 font-medium text-ink" : "text-ink-2 hover:bg-surface-2/70 hover:text-ink",
      )}
    >
      <Icon className={cn("size-4", active ? "text-brand" : "text-muted")} aria-hidden />
      <span className="flex-1 truncate">{label}</span>
      {!!count && (
        <span className="tabular min-w-5 rounded-full bg-brand px-1.5 text-center text-[11px] font-semibold leading-5 text-brand-ink">
          {count > 99 ? "99+" : count}
          <span className="sr-only"> okunmamış</span>
        </span>
      )}
    </Link>
  );
}

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const router = useRouter();
  const me = useMe();
  const subjects = useSubjects();
  const conversations = useConversations();
  const notifications = useNotifications();
  const logout = useLogout();

  const unreadMessages = conversations.data?.reduce((sum, c) => sum + c.unread, 0) ?? 0;
  const unreadNotifications = notifications.data?.filter((n) => !n.read_at).length ?? 0;
  const user = me.data;
  const subjectsTitle = user?.role === "doctor" ? "Danışanlar" : user?.role === "parent" ? "Çocuklarım" : "Takibim";

  return (
    <div className="flex h-full flex-col" onClick={(e) => (e.target as HTMLElement).closest("a") && onNavigate?.()}>
      <div className="px-4 pt-5 pb-4">
        <Logo href="/dashboard" />
      </div>

      <nav className="flex-1 space-y-6 overflow-y-auto px-3" aria-label="Ana menü">
        <div className="space-y-0.5">
          <NavItem href="/dashboard" icon={LayoutDashboard} label="Genel bakış" active={pathname === "/dashboard"} />
          <NavItem
            href="/messages"
            icon={MessageSquare}
            label="Mesajlar"
            count={unreadMessages}
            active={pathname.startsWith("/messages")}
          />
          <NavItem
            href="/notifications"
            icon={Bell}
            label="Bildirimler"
            count={unreadNotifications}
            active={pathname.startsWith("/notifications")}
          />
          <NavItem href="/assistant" icon={Sparkles} label="Deva asistan" active={pathname.startsWith("/assistant")} />
        </div>

        <div>
          <p className="px-2.5 pb-1.5 text-xs font-medium text-muted">{subjectsTitle}</p>
          <div className="space-y-0.5">
            {subjects.isPending && <Skeleton className="mx-2.5 h-7" />}
            {subjects.data?.map((subject) => {
              const href = `/subjects/${subject.id}`;
              return (
                <Link
                  key={subject.id}
                  href={href}
                  aria-current={pathname.startsWith(href) ? "page" : undefined}
                  className={cn(
                    "flex h-9 items-center gap-2.5 rounded-lg px-2.5 text-sm transition-colors",
                    pathname.startsWith(href)
                      ? "bg-surface-2 font-medium text-ink"
                      : "text-ink-2 hover:bg-surface-2/70 hover:text-ink",
                  )}
                >
                  <Avatar name={subject.name} className="size-6 text-[10px]" />
                  <span className="flex-1 truncate">{subject.kind === "self" && subject.owner.id === user?.id ? "Benim takibim" : subject.name}</span>
                  {subject.summary.alert_count > 0 && (
                    <span className="size-2 rounded-full bg-warning" aria-label={`${subject.summary.alert_count} uyarı`} />
                  )}
                </Link>
              );
            })}
            {subjects.data?.length === 0 && (
              <p className="px-2.5 text-xs text-muted">
                {user?.role === "doctor" ? "Henüz sizi ekleyen danışan yok." : "Henüz kayıt yok."}
              </p>
            )}
          </div>
        </div>

        <div>
          <p className="px-2.5 pb-1.5 text-xs font-medium text-muted">Şeffaflık</p>
          <NavItem href="/model" icon={BrainCircuit} label="Model kartı" active={pathname.startsWith("/model")} />
        </div>
      </nav>

      <div className="border-t border-line p-3">
        <div className="flex items-center gap-2.5 rounded-lg px-1.5 py-1.5">
          {user ? <Avatar name={user.full_name} /> : <Skeleton className="size-9 rounded-full" />}
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user?.full_name ?? "…"}</p>
            <p className="truncate text-xs text-muted">{user ? ROLE_LABEL[user.role] : ""}</p>
          </div>
          <ThemeToggle />
          <Button
            variant="ghost"
            size="icon"
            aria-label="Çıkış yap"
            title="Çıkış yap"
            onClick={() => logout.mutate(undefined, { onSettled: () => router.replace("/login") })}
          >
            <LogOut className="size-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function SidebarFallback() {
  return (
    <div className="space-y-3 px-4 pt-5">
      <Logo href="/dashboard" />
      <Skeleton className="mt-4 h-8" />
      <Skeleton className="h-8" />
      <Skeleton className="h-8" />
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
  }, [open]);

  return (
    <div className="min-h-dvh lg:grid lg:grid-cols-[260px_1fr]">
      <aside className="sticky top-0 hidden h-dvh border-r border-line bg-surface lg:block">
        <Suspense fallback={<SidebarFallback />}>
          <Sidebar />
        </Suspense>
      </aside>

      <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-line bg-surface/90 px-4 backdrop-blur lg:hidden">
        <Logo href="/dashboard" />
        <Button variant="ghost" size="icon" aria-label="Menüyü aç" aria-expanded={open} onClick={() => setOpen(true)}>
          <Menu className="size-5" />
        </Button>
      </header>

      {open && (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Menü">
          <div className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 w-[84%] max-w-[300px] bg-surface shadow-2xl">
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-4 right-3"
              aria-label="Menüyü kapat"
              onClick={() => setOpen(false)}
            >
              <X className="size-5" />
            </Button>
            <Suspense fallback={<SidebarFallback />}>
              <Sidebar onNavigate={() => setOpen(false)} />
            </Suspense>
          </div>
        </div>
      )}

      <main className="min-w-0 px-4 py-6 sm:px-8 sm:py-8">
        <div className="mx-auto max-w-6xl">
          <Suspense fallback={<Spinner />}>{children}</Suspense>
        </div>
      </main>
    </div>
  );
}
