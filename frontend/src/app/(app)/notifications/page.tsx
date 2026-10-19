"use client";

import {
  AlertOctagon,
  Bell,
  CalendarClock,
  ClipboardCheck,
  ClipboardList,
  FileText,
  MessageSquare,
  ShieldCheck,
  UserPlus,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";

import { Button, Card, EmptyState, ErrorState, PageHeader, Spinner } from "@/components/ui";
import { cn } from "@/lib/cn";
import { formatRelative } from "@/lib/format";
import { useMarkNotification, useNotifications } from "@/lib/queries";

const ICON: Record<string, LucideIcon> = {
  message: MessageSquare,
  note: FileText,
  observation: FileText,
  care_team: UserPlus,
  screening: ClipboardList,
  risk: AlertOctagon,
  visit: CalendarClock,
  doctor_application: ClipboardCheck,
  account: ShieldCheck,
};

export default function NotificationsPage() {
  const notifications = useNotifications();
  const mark = useMarkNotification();
  const unread = notifications.data?.filter((n) => !n.read_at).length ?? 0;

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title="Bildirimler"
        description={unread ? `${unread} okunmamış bildirim` : "Hepsi okundu"}
        action={
          unread > 0 && (
            <Button variant="secondary" onClick={() => mark.mutate("all")} loading={mark.isPending && mark.variables === "all"}>
              Tümünü okundu işaretle
            </Button>
          )
        }
      />
      {notifications.isPending ? (
        <Spinner />
      ) : notifications.error ? (
        <ErrorState error={notifications.error} />
      ) : notifications.data.length === 0 ? (
        <Card>
          <EmptyState icon={<Bell className="size-5" />} title="Bildirim yok" />
        </Card>
      ) : (
        <Card>
          <ul className="divide-y divide-line">
            {notifications.data.map((n) => {
              const Icon = ICON[n.kind] ?? Bell;
              const content = (
                <>
                  <span
                    className={cn(
                      "grid size-9 shrink-0 place-items-center rounded-xl",
                      n.kind === "risk" ? "bg-critical-soft text-critical-ink" : "bg-surface-2 text-ink-2",
                    )}
                  >
                    <Icon className="size-4" aria-hidden />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className={cn("text-sm", n.read_at ? "font-medium text-ink-2" : "font-semibold")}>{n.title}</p>
                    <p className="text-sm text-muted">{n.body}</p>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1.5">
                    <span className="text-xs text-muted">{formatRelative(n.created_at)}</span>
                    {!n.read_at && <span className="size-2 rounded-full bg-brand" aria-label="Okunmadı" />}
                  </div>
                </>
              );
              const className = "flex gap-3 px-5 py-4 transition-colors hover:bg-surface-2/60";
              const markRead = () => !n.read_at && mark.mutate(n.id);
              return (
                <li key={n.id}>
                  {n.link ? (
                    <Link href={n.link} className={className} onClick={markRead}>
                      {content}
                    </Link>
                  ) : (
                    <button className={cn(className, "w-full text-left")} onClick={markRead}>
                      {content}
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        </Card>
      )}
    </div>
  );
}
