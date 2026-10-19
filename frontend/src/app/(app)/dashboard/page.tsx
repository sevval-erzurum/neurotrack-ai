"use client";

import {
  AlertTriangle,
  ArrowRight,
  Baby,
  CalendarClock,
  CheckCircle2,
  Flame,
  MessageSquare,
  Plus,
  Users,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { AdminDashboard, DoctorStatusPanel } from "@/components/admin";
import { AddChildDialog, DailyLogDialog } from "@/components/forms";
import {
  Avatar,
  Badge,
  Button,
  ButtonLink,
  Card,
  CardHeader,
  EmptyState,
  ErrorState,
  PageHeader,
  RiskBadge,
  Skeleton,
} from "@/components/ui";
import { formatAge, formatDay, formatRelative, todayISO } from "@/lib/format";
import { useConversations, useInsights, useMe, useNotifications, useSubjects } from "@/lib/queries";
import type { RiskLevel, SubjectWithSummary, User } from "@/lib/types";

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 6) return "İyi geceler";
  if (hour < 12) return "Günaydın";
  if (hour < 18) return "İyi günler";
  return "İyi akşamlar";
}

export default function DashboardPage() {
  const me = useMe();
  const subjects = useSubjects();

  if (me.isPending || subjects.isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-9 w-64" />
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-56" />
          <Skeleton className="h-56" />
        </div>
      </div>
    );
  }
  if (me.error || subjects.error) return <ErrorState error={me.error ?? subjects.error} retry={() => subjects.refetch()} />;

  if (me.data.role === "admin") return <AdminDashboard user={me.data} />;
  if (me.data.role === "doctor" && me.data.doctor_status !== "approved") return <DoctorStatusPanel user={me.data} />;
  return me.data.role === "doctor" ? (
    <DoctorDashboard user={me.data} subjects={subjects.data} />
  ) : (
    <FamilyDashboard user={me.data} subjects={subjects.data} />
  );
}

// --- Ebeveyn / yetişkin -------------------------------------------------------

function FamilyDashboard({ user, subjects }: { user: User; subjects: SubjectWithSummary[] }) {
  const [addChild, setAddChild] = useState(false);
  const firstName = user.full_name.split(" ")[0];

  return (
    <>
      <PageHeader
        title={`${greeting()}, ${firstName}`}
        description={
          user.role === "parent" ? "Çocuklarınızın bugünkü durumu ve bekleyen işler." : "Bugünkü durumunuz ve bekleyen işler."
        }
        action={
          user.role === "parent" && (
            <Button onClick={() => setAddChild(true)}>
              <Plus className="size-4" aria-hidden />
              Çocuk ekle
            </Button>
          )
        }
      />

      {subjects.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Baby className="size-5" />}
            title="Henüz bir çocuk eklemediniz"
            description="Takibe başlamak için çocuğunuzu ekleyin. 18–24 aylık çocuklar için Q-CHAT taraması yapılabilir."
            action={<Button onClick={() => setAddChild(true)}>Çocuk ekle</Button>}
          />
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {subjects.map((subject) => (
            <SubjectCard key={subject.id} subject={subject} />
          ))}
        </div>
      )}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <RecentNotifications />
        <CareTeamCard subjects={subjects} />
      </div>

      <AddChildDialog open={addChild} onClose={() => setAddChild(false)} />
    </>
  );
}

function SubjectCard({ subject }: { subject: SubjectWithSummary }) {
  const insights = useInsights(subject.id, 7);
  const [logOpen, setLogOpen] = useState(false);
  const loggedToday = subject.summary.last_log_date === todayISO();
  const stats = insights.data?.stats;
  const title = subject.kind === "self" ? "Benim takibim" : subject.name;

  return (
    <Card className="flex flex-col">
      <div className="flex items-start gap-3 p-5 pb-4">
        <Avatar name={subject.name} className="size-11 text-sm" />
        <div className="min-w-0 flex-1">
          <Link href={`/subjects/${subject.id}`} className="font-semibold tracking-tight hover:underline">
            {title}
          </Link>
          <p className="text-sm text-muted">
            {subject.kind === "child" ? formatAge(subject.age_months) : "Yetişkin"}
            {subject.care_team.length > 0 && ` · ${subject.care_team.map((d) => d.full_name).join(", ")}`}
          </p>
        </div>
        {subject.summary.latest_risk && <RiskBadge level={subject.summary.latest_risk} />}
      </div>

      <dl className="grid grid-cols-3 border-y border-line">
        <Stat label="Seri" value={stats ? `${stats.streak} gün` : "—"} icon={<Flame className="size-3.5" aria-hidden />} />
        <Stat label="Ort. uyku (7g)" value={stats?.avg_sleep != null ? `${stats.avg_sleep} sa` : "—"} />
        <Stat label="Sosyal (7g)" value={stats?.avg_social != null ? `${stats.avg_social}/10` : "—"} />
      </dl>

      <div className="flex flex-1 flex-col gap-3 p-5">
        {subject.summary.alert_count > 0 ? (
          <div className="flex items-center gap-2 text-sm text-warning-ink">
            <AlertTriangle className="size-4" aria-hidden />
            {subject.summary.alert_count} takip uyarısı var
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-good-ink">
            <CheckCircle2 className="size-4" aria-hidden />
            Dikkat gerektiren uyarı yok
          </div>
        )}
        {subject.summary.next_visit && (
          <div className="flex items-center gap-2 text-sm text-ink-2">
            <CalendarClock className="size-4 text-muted" aria-hidden />
            Sonraki görüşme: {formatDay(subject.summary.next_visit)}
          </div>
        )}
        <div className="mt-auto flex flex-wrap gap-2 pt-2">
          {loggedToday ? (
            <Badge tone="good" className="h-8 px-3">
              <CheckCircle2 className="size-3.5" aria-hidden />
              Bugünün kaydı girildi
            </Badge>
          ) : (
            <Button size="sm" variant="brand" onClick={() => setLogOpen(true)}>
              <Plus className="size-4" aria-hidden />
              Bugünün kaydını ekle
            </Button>
          )}
          <ButtonLink size="sm" variant="secondary" href={`/subjects/${subject.id}`}>
            Ayrıntılar
            <ArrowRight className="size-4" aria-hidden />
          </ButtonLink>
        </div>
      </div>

      {logOpen && (
        <DailyLogDialog subjectId={subject.id} subjectName={title} open onClose={() => setLogOpen(false)} />
      )}
    </Card>
  );
}

function Stat({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="border-line px-5 py-3 not-last:border-r">
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="tabular mt-0.5 flex items-center gap-1 text-[15px] font-semibold">
        {icon}
        {value}
      </dd>
    </div>
  );
}

function RecentNotifications() {
  const notifications = useNotifications();
  const items = notifications.data?.slice(0, 4) ?? [];
  return (
    <Card>
      <CardHeader
        title="Son bildirimler"
        action={
          <Link href="/notifications" className="text-sm text-brand hover:underline">
            Tümü
          </Link>
        }
      />
      <ul className="divide-y divide-line px-5 pb-2">
        {notifications.isPending && <Skeleton className="my-4 h-10" />}
        {items.map((n) => (
          <li key={n.id} className="flex gap-3 py-3">
            <span className={`mt-1.5 size-2 shrink-0 rounded-full ${n.read_at ? "bg-transparent" : "bg-brand"}`} aria-hidden />
            <div className="min-w-0">
              <p className="text-sm font-medium">{n.title}</p>
              <p className="truncate text-sm text-ink-2">{n.body}</p>
            </div>
            <span className="ml-auto shrink-0 text-xs text-muted">{formatRelative(n.created_at)}</span>
          </li>
        ))}
        {notifications.data?.length === 0 && <p className="py-6 text-center text-sm text-muted">Bildirim yok.</p>}
      </ul>
    </Card>
  );
}

function CareTeamCard({ subjects }: { subjects: SubjectWithSummary[] }) {
  const doctors = new Map(subjects.flatMap((s) => s.care_team.map((d) => [d.id, d] as const)));
  return (
    <Card>
      <CardHeader title="Bakım ekibi" description="Verilerinizi yalnızca buradaki doktorlar görebilir." />
      <div className="p-5 pt-4">
        {doctors.size === 0 ? (
          <p className="text-sm text-ink-2">
            Henüz doktor eklemediniz. Bir kişinin sayfasındaki <b>Bakım ekibi</b> sekmesinden doktorunuzu e-postasıyla
            ekleyebilirsiniz.
          </p>
        ) : (
          <ul className="space-y-3">
            {[...doctors.values()].map((d) => (
              <li key={d.id} className="flex items-center gap-3">
                <Avatar name={d.full_name} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{d.full_name}</p>
                  <p className="truncate text-xs text-muted">{d.email}</p>
                </div>
                <ButtonLink size="sm" variant="secondary" href={`/messages?with=${d.id}`}>
                  <MessageSquare className="size-4" aria-hidden />
                  Mesaj
                </ButtonLink>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}

// --- Doktor -----------------------------------------------------------------------

const RISK_ORDER: Record<RiskLevel, number> = { high: 0, elevated: 1, low: 2 };

function DoctorDashboard({ user, subjects }: { user: User; subjects: SubjectWithSummary[] }) {
  const conversations = useConversations();
  const unread = conversations.data?.reduce((s, c) => s + c.unread, 0) ?? 0;
  const withAlerts = subjects.filter((s) => s.summary.alert_count > 0).length;
  const upcoming = subjects
    .filter((s) => s.summary.next_visit)
    .sort((a, b) => a.summary.next_visit!.localeCompare(b.summary.next_visit!));

  // Önce uyarısı olanlar, sonra risk düzeyi.
  const sorted = [...subjects].sort(
    (a, b) =>
      b.summary.alert_count - a.summary.alert_count ||
      (RISK_ORDER[a.summary.latest_risk ?? "low"] ?? 3) - (RISK_ORDER[b.summary.latest_risk ?? "low"] ?? 3),
  );

  return (
    <>
      <PageHeader title={`${greeting()}, ${user.full_name}`} description="Danışanlarınızın güncel durumu, önceliğe göre sıralı." />

      <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Tile label="Danışan" value={subjects.length} icon={<Users className="size-4" aria-hidden />} />
        <Tile label="Uyarısı olan" value={withAlerts} icon={<AlertTriangle className="size-4" aria-hidden />} />
        <Tile label="Okunmamış mesaj" value={unread} icon={<MessageSquare className="size-4" aria-hidden />} href="/messages" />
        <Tile
          label="Sıradaki görüşme"
          value={upcoming[0] ? formatDay(upcoming[0].summary.next_visit!) : "—"}
          icon={<CalendarClock className="size-4" aria-hidden />}
          small
        />
      </div>

      <Card>
        <CardHeader title="Danışanlar" description="Danışanlar sizi kendi bakım ekiplerine ekler; ekleme yetkisi onlardadır." />
        {subjects.length === 0 ? (
          <EmptyState
            icon={<Users className="size-5" />}
            title="Henüz danışanınız yok"
            description="Danışanlarınız sizi e-posta adresinizle bakım ekiplerine eklediğinde burada görünür."
          />
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-y border-line text-left text-xs text-muted">
                  <th className="px-5 py-2.5 font-medium">Danışan</th>
                  <th className="px-3 py-2.5 font-medium">Son tarama</th>
                  <th className="px-3 py-2.5 font-medium">Uyarı</th>
                  <th className="px-3 py-2.5 font-medium">Son kayıt</th>
                  <th className="px-3 py-2.5 font-medium">Görüşme</th>
                  <th className="px-5 py-2.5" />
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {sorted.map((s) => (
                  <tr key={s.id} className="transition-colors hover:bg-surface-2/60">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-3">
                        <Avatar name={s.name} />
                        <div>
                          <p className="font-medium">{s.name}</p>
                          <p className="text-xs text-muted">
                            {s.kind === "child" ? `${formatAge(s.age_months)} · Veli: ${s.owner.full_name}` : "Yetişkin"}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-3">
                      {s.summary.latest_risk ? <RiskBadge level={s.summary.latest_risk} /> : <span className="text-muted">—</span>}
                    </td>
                    <td className="tabular px-3 py-3">
                      {s.summary.alert_count > 0 ? (
                        <Badge tone="warning">
                          <AlertTriangle className="size-3.5" aria-hidden />
                          {s.summary.alert_count}
                        </Badge>
                      ) : (
                        <span className="text-muted">0</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-ink-2">
                      {s.summary.last_log_date ? formatDay(s.summary.last_log_date) : "—"}
                    </td>
                    <td className="px-3 py-3 text-ink-2">
                      {s.summary.next_visit ? formatDay(s.summary.next_visit) : "—"}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <ButtonLink size="sm" variant="secondary" href={`/subjects/${s.id}`}>
                        Aç
                      </ButtonLink>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}

function Tile({
  label,
  value,
  icon,
  href,
  small,
}: {
  label: string;
  value: React.ReactNode;
  icon: React.ReactNode;
  href?: string;
  small?: boolean;
}) {
  const body = (
    <Card className="h-full p-4 transition-colors hover:border-line-strong">
      <div className="flex items-center gap-2 text-sm text-muted">
        {icon}
        {label}
      </div>
      <p className={`tabular mt-2 font-semibold tracking-tight ${small ? "text-base" : "text-2xl"}`}>{value}</p>
    </Card>
  );
  return href ? <Link href={href}>{body}</Link> : body;
}
