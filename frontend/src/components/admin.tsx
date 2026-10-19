"use client";

import { Ban, CheckCircle2, ClipboardCheck, Hourglass, ScrollText, ShieldAlert, ShieldCheck, XCircle } from "lucide-react";
import Link from "next/link";

import { DOCTOR_STATUS_LABEL, ROLE_LABEL, actionLabel, formatRelative } from "@/lib/format";
import { useAdminOverview, useAuditEvents, useDoctorApplications } from "@/lib/queries";
import type { DoctorStatus, Role, User } from "@/lib/types";

import { Badge, ButtonLink, Card, CardHeader, EmptyState, ErrorState, PageHeader, Skeleton } from "./ui";

const STATUS_STYLE: Record<DoctorStatus, { tone: "warning" | "good" | "critical" | "neutral"; icon: typeof Hourglass }> = {
  pending: { tone: "warning", icon: Hourglass },
  approved: { tone: "good", icon: CheckCircle2 },
  rejected: { tone: "critical", icon: XCircle },
  suspended: { tone: "neutral", icon: Ban },
};

/** Durum her zaman ikon + metinle gösterilir; renk tek başına anlam taşımaz. */
export function DoctorStatusBadge({ status }: { status: DoctorStatus }) {
  const { tone, icon: Icon } = STATUS_STYLE[status];
  return (
    <Badge tone={tone}>
      <Icon className="size-3.5" aria-hidden />
      {DOCTOR_STATUS_LABEL[status]}
    </Badge>
  );
}

export function AdminOnly({ user, children }: { user: User | undefined; children: React.ReactNode }) {
  if (user && user.role !== "admin") {
    return (
      <Card>
        <EmptyState
          icon={<ShieldAlert className="size-5" />}
          title="Bu sayfa yöneticiler içindir"
          action={<ButtonLink href="/dashboard" variant="secondary" size="sm">Genel bakışa dön</ButtonLink>}
        />
      </Card>
    );
  }
  return children;
}

// --- Yönetici genel bakış -----------------------------------------------------

function Stat({ label, value, sub, href }: { label: string; value: number | string; sub?: string; href?: string }) {
  const body = (
    <>
      <p className="text-sm text-muted">{label}</p>
      <p className="tabular mt-1.5 text-2xl font-semibold tracking-tight">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-muted">{sub}</p>}
    </>
  );
  return href ? (
    <Link href={href} className="rounded-card border border-line bg-surface p-4 shadow-card transition-colors hover:border-line-strong">
      {body}
    </Link>
  ) : (
    <Card className="p-4">{body}</Card>
  );
}

export function AdminDashboard({ user }: { user: User }) {
  const overview = useAdminOverview();
  const pending = useDoctorApplications("pending");
  const denied = useAuditEvents({ outcome: "denied" });

  if (overview.isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-9 w-64" />
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>
    );
  }
  if (overview.error) return <ErrorState error={overview.error} retry={() => overview.refetch()} />;

  const o = overview.data;
  const totalUsers = Object.values(o.users_by_role).reduce((a, b) => a + (b ?? 0), 0);
  const recentDenied = denied.data?.pages[0]?.items.slice(0, 6) ?? [];

  return (
    <>
      <PageHeader
        title="Yönetim paneli"
        description={`${user.full_name} olarak oturum açtınız. Yönetici hesabı danışan sağlık verilerini göremez.`}
      />

      <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat
          label="Onay bekleyen doktor"
          value={o.doctors_by_status.pending ?? 0}
          sub="İncelemek için tıklayın"
          href="/admin/doctors"
        />
        <Stat
          label="Kullanıcı"
          value={totalUsers}
          sub={(["parent", "adult", "doctor"] as Role[]).map((r) => `${o.users_by_role[r] ?? 0} ${ROLE_LABEL[r].toLowerCase()}`).join(" · ")}
        />
        <Stat label="Reddedilen erişim (24 sa)" value={o.denied_last_24h} sub="Yetkisiz kayıt denemeleri" href="/admin/audit?outcome=denied" />
        <Stat label="Başarısız giriş (24 sa)" value={o.failed_logins_last_24h} sub={`Toplam ${o.events_last_24h} olay`} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader
            title="Bekleyen başvurular"
            action={<ButtonLink href="/admin/doctors" variant="ghost" size="sm">Tümü</ButtonLink>}
          />
          <ul className="divide-y divide-line px-5 py-2">
            {pending.data?.length === 0 && (
              <li className="flex items-center gap-2 py-6 text-sm text-muted">
                <ShieldCheck className="size-4 text-good" aria-hidden /> Bekleyen başvuru yok.
              </li>
            )}
            {pending.data?.slice(0, 5).map((d) => (
              <li key={d.id} className="flex items-center gap-3 py-3">
                <ClipboardCheck className="size-4 text-muted" aria-hidden />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{d.full_name}</p>
                  <p className="truncate text-xs text-muted">
                    {d.institution} · {formatRelative(d.created_at)}
                  </p>
                </div>
                <DoctorStatusBadge status={d.doctor_status} />
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <CardHeader
            title="Son reddedilen erişimler"
            description="Yetkisi olmayan bir kayda veya yönetim ucuna yapılan istekler"
            action={<ButtonLink href="/admin/audit?outcome=denied" variant="ghost" size="sm">Günlük</ButtonLink>}
          />
          <ul className="divide-y divide-line px-5 py-2">
            {recentDenied.length === 0 && <li className="py-6 text-sm text-muted">Kayıt yok.</li>}
            {recentDenied.map((e) => (
              <li key={e.id} className="flex items-center gap-3 py-3">
                <ScrollText className="size-4 text-muted" aria-hidden />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm">
                    <span className="font-medium">{e.actor_label ?? "Anonim"}</span> · {actionLabel(e.action)}
                  </p>
                  <p className="text-xs text-muted">
                    {formatRelative(e.created_at)}
                    {e.subject_id !== null && ` · kayıt #${e.subject_id}`}
                  </p>
                </div>
                <Badge tone="critical">{e.status_code}</Badge>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </>
  );
}

// --- Onaylanmamış doktor -------------------------------------------------------

const DOCTOR_PANEL: Record<Exclude<DoctorStatus, "approved">, { title: string; text: string; icon: typeof Hourglass }> = {
  pending: {
    title: "Başvurunuz inceleniyor",
    text: "Diploma tescil numaranız ve kurum bilginiz bir yönetici tarafından doğrulanıyor. Onaylandığınızda bildirim alacaksınız; danışanlar ancak bundan sonra sizi bakım ekiplerine ekleyebilir.",
    icon: Hourglass,
  },
  rejected: {
    title: "Başvurunuz reddedildi",
    text: "Bilgileriniz doğrulanamadı. Hatalı bir bilgi olduğunu düşünüyorsanız kurumunuz üzerinden destek ekibimizle iletişime geçin.",
    icon: XCircle,
  },
  suspended: {
    title: "Hesabınız askıya alındı",
    text: "Danışan verilerine erişiminiz durduruldu. Bakım ekibi kayıtlarınız silinmedi; hesabınız yeniden onaylanırsa erişiminiz geri gelir.",
    icon: Ban,
  },
};

export function DoctorStatusPanel({ user }: { user: User }) {
  const status = (user.doctor_status ?? "pending") as Exclude<DoctorStatus, "approved">;
  const { title, text, icon: Icon } = DOCTOR_PANEL[status];
  return (
    <>
      <PageHeader title={`Merhaba, ${user.full_name}`} description="Doktor hesabınızın durumu" />
      <Card className="max-w-2xl p-6">
        <div className="flex items-start gap-4">
          <div className="grid size-11 shrink-0 place-items-center rounded-2xl bg-surface-2 text-ink-2">
            <Icon className="size-5" aria-hidden />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="font-semibold tracking-tight">{title}</h2>
              <DoctorStatusBadge status={status} />
            </div>
            <p className="mt-2 text-sm leading-relaxed text-ink-2">{text}</p>
            {user.status_reason && (
              <p className="mt-3 rounded-xl bg-surface-2 px-3 py-2.5 text-sm">
                <span className="font-medium">Yönetici notu:</span> {user.status_reason}
              </p>
            )}
          </div>
        </div>
      </Card>
    </>
  );
}
