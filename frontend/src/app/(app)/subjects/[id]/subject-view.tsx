"use client";

import {
  CalendarClock,
  ClipboardList,
  FileText,
  Microscope,
  Pencil,
  Plus,
  Stethoscope,
  Trash2,
  UserPlus,
  X,
} from "lucide-react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { MoodStrip, TrendChart } from "@/components/charts";
import { DailyLogDialog, MOOD_ICON, NoteDialog, ObservationDialog } from "@/components/forms";
import {
  AlertList,
  Avatar,
  Badge,
  Button,
  ButtonLink,
  Card,
  CardHeader,
  EmptyState,
  ErrorState,
  Field,
  Input,
  PageHeader,
  RiskBadge,
  Skeleton,
  Spinner,
} from "@/components/ui";
import { cn } from "@/lib/cn";
import { INSTRUMENT_LABEL, formatAge, formatDate, formatDay, moodOf } from "@/lib/format";
import {
  useAddDoctor,
  useDeleteLog,
  useDeleteSubject,
  useInsights,
  useLogs,
  useMe,
  useNotes,
  useObservations,
  useRemoveDoctor,
  useScreenings,
  useSubject,
} from "@/lib/queries";
import type { DailyLog, Subject, User } from "@/lib/types";

const TABS = [
  { key: "overview", label: "Genel bakış" },
  { key: "logs", label: "Günlük kayıtlar" },
  { key: "screenings", label: "Taramalar" },
  { key: "observations", label: "Klinik gözlemler" },
  { key: "notes", label: "Doktor notları" },
  { key: "team", label: "Bakım ekibi" },
] as const;
type Tab = (typeof TABS)[number]["key"];

export function SubjectView() {
  const id = Number(useParams<{ id: string }>().id);
  const params = useSearchParams();
  const router = useRouter();
  const tab = (TABS.find((t) => t.key === params.get("tab"))?.key ?? "overview") as Tab;
  const me = useMe();
  const subject = useSubject(id);
  const [logOpen, setLogOpen] = useState(false);

  if (subject.isPending || me.isPending) return <Spinner />;
  if (subject.error || me.error) return <ErrorState error={subject.error ?? me.error} retry={() => subject.refetch()} />;

  const s = subject.data;
  const user = me.data;
  const isOwner = s.owner.id === user.id;
  const title = s.kind === "self" && isOwner ? "Benim takibim" : s.name;

  return (
    <>
      <PageHeader
        eyebrow={
          <span className="inline-flex items-center gap-2">
            <Link href="/dashboard" className="hover:text-ink">
              Genel bakış
            </Link>
            <span aria-hidden>/</span>
            <span>{title}</span>
          </span>
        }
        title={
          <span className="flex items-center gap-3">
            <Avatar name={s.name} className="size-10 text-sm" />
            {title}
          </span>
        }
        description={
          s.kind === "child"
            ? `${formatAge(s.age_months)}${s.birth_date ? ` · Doğum: ${formatDay(s.birth_date)}` : ""}${isOwner ? "" : ` · Veli: ${s.owner.full_name}`}`
            : isOwner
              ? "Kendi günlük takibiniz ve taramalarınız"
              : "Yetişkin danışan"
        }
        action={
          <>
            {isOwner && (
              <Button variant="brand" onClick={() => setLogOpen(true)}>
                <Plus className="size-4" aria-hidden />
                Günlük kayıt
              </Button>
            )}
            <ButtonLink variant="secondary" href={`/subjects/${id}/screening`}>
              <ClipboardList className="size-4" aria-hidden />
              Tarama yap
            </ButtonLink>
          </>
        }
      />

      <div className="-mx-4 mb-6 overflow-x-auto px-4 sm:mx-0 sm:px-0">
        <div role="tablist" aria-label="Bölümler" className="flex min-w-max gap-1 border-b border-line">
          {TABS.map((t) => (
            <button
              key={t.key}
              role="tab"
              aria-selected={tab === t.key}
              onClick={() => router.replace(t.key === "overview" ? `/subjects/${id}` : `/subjects/${id}?tab=${t.key}`, { scroll: false })}
              className={cn(
                "-mb-px border-b-2 px-3 py-2.5 text-sm transition-colors",
                tab === t.key ? "border-brand font-medium text-ink" : "border-transparent text-muted hover:text-ink",
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div role="tabpanel">
        {tab === "overview" && <Overview subjectId={id} />}
        {tab === "logs" && <Logs subject={s} isOwner={isOwner} />}
        {tab === "screenings" && <Screenings subjectId={id} />}
        {tab === "observations" && <Observations subjectId={id} />}
        {tab === "notes" && <Notes subjectId={id} user={user} />}
        {tab === "team" && <Team subject={s} user={user} />}
      </div>

      {logOpen && <DailyLogDialog subjectId={id} subjectName={title} open onClose={() => setLogOpen(false)} />}
    </>
  );
}

// --- Genel bakış -------------------------------------------------------------------

function Overview({ subjectId }: { subjectId: number }) {
  const [days, setDays] = useState(30);
  const insights = useInsights(subjectId, days);

  if (insights.isPending) {
    return (
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-64" />
        <Skeleton className="h-64" />
      </div>
    );
  }
  if (insights.error) return <ErrorState error={insights.error} retry={() => insights.refetch()} />;

  const { stats, series, alerts, latest_screening, next_visit } = insights.data;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted">Son {days} gün</p>
        <div className="inline-flex rounded-xl border border-line bg-surface p-0.5" role="group" aria-label="Zaman aralığı">
          {[14, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              aria-pressed={days === d}
              className={cn(
                "rounded-[10px] px-3 py-1 text-sm transition-colors",
                days === d ? "bg-surface-2 font-medium text-ink" : "text-muted hover:text-ink",
              )}
            >
              {d} gün
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Kayıt" value={`${stats.n_logs}`} sub={`${stats.streak} günlük seri`} />
        <StatTile label="Ortalama uyku" value={stats.avg_sleep != null ? `${stats.avg_sleep} sa` : "—"} />
        <StatTile label="Ortalama sosyal" value={stats.avg_social != null ? `${stats.avg_social}/10` : "—"} />
        <StatTile label="Kriz yaşanan gün" value={`${stats.meltdown_days}`} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_340px]">
        <div className="space-y-4">
          {series.length === 0 ? (
            <Card>
              <EmptyState
                icon={<FileText className="size-5" />}
                title="Bu aralıkta kayıt yok"
                description="Günlük kayıt eklendikçe uyku, sosyal etkileşim ve duygu durumu eğilimleri burada görünür."
              />
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader title="Uyku süresi" description="Saat / gece" />
                <div className="px-3 pt-3 pb-4">
                  <TrendChart
                    data={series}
                    dataKey="sleep_hours"
                    domain={[0, 12]}
                    unit=" saat"
                    reference={{ y: 6, label: "6 sa" }}
                    ariaLabel={`Uyku süresi grafiği, ortalama ${stats.avg_sleep} saat`}
                  />
                </div>
              </Card>
              <Card>
                <CardHeader title="Sosyal etkileşim" description="0–10 ölçeği" />
                <div className="px-3 pt-3 pb-4">
                  <TrendChart
                    data={series}
                    dataKey="social_interaction"
                    domain={[0, 10]}
                    unit="/10"
                    reference={{ y: 4, label: "4" }}
                    ariaLabel={`Sosyal etkileşim grafiği, ortalama ${stats.avg_social}`}
                  />
                </div>
              </Card>
              <Card>
                <CardHeader title="Duygu durumu" description={`Son ${Math.min(days, 30)} gün, günlük`} />
                <div className="p-5 pt-4">
                  <MoodStrip series={series} days={Math.min(days, 30)} />
                </div>
              </Card>
            </>
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader title="Takip uyarıları" description="Son 7 günün kayıtlarından, kural tabanlı" />
            <div className="p-5 pt-4">
              <AlertList alerts={alerts} />
            </div>
          </Card>

          <Card>
            <CardHeader title="Son tarama" />
            <div className="p-5 pt-3">
              {latest_screening ? (
                <Link
                  href={`/subjects/${subjectId}/screenings/${latest_screening.id}`}
                  className="block rounded-xl border border-line p-3.5 transition-colors hover:bg-surface-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium">{INSTRUMENT_LABEL[latest_screening.instrument]}</span>
                    <RiskBadge level={latest_screening.risk_level} />
                  </div>
                  <p className="mt-1 text-xs text-muted">{formatDate(latest_screening.created_at)}</p>
                </Link>
              ) : (
                <p className="text-sm text-muted">Henüz tarama yapılmadı.</p>
              )}
            </div>
          </Card>

          {next_visit && (
            <Card className="flex items-center gap-3 p-4">
              <span className="grid size-10 place-items-center rounded-xl bg-info-soft text-info-ink">
                <CalendarClock className="size-5" aria-hidden />
              </span>
              <div>
                <p className="text-xs text-muted">Sonraki görüşme</p>
                <p className="font-medium">{formatDay(next_visit)}</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function StatTile({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <Card className="p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="tabular mt-1.5 text-2xl font-semibold tracking-tight">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-muted">{sub}</p>}
    </Card>
  );
}

// --- Günlük kayıtlar --------------------------------------------------------------

function Logs({ subject, isOwner }: { subject: Subject; isOwner: boolean }) {
  const logs = useLogs(subject.id);
  const remove = useDeleteLog(subject.id);
  const [editing, setEditing] = useState<DailyLog | null>(null);

  if (logs.isPending) return <Spinner />;
  if (logs.error) return <ErrorState error={logs.error} retry={() => logs.refetch()} />;
  if (!logs.data.length) {
    return (
      <Card>
        <EmptyState icon={<FileText className="size-5" />} title="Henüz günlük kayıt yok" />
      </Card>
    );
  }

  return (
    <Card>
      <ul className="divide-y divide-line">
        {logs.data.map((log) => {
          const mood = moodOf(log.mood);
          const Icon = MOOD_ICON[log.mood];
          return (
            <li key={log.id} className="flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-3.5">
              <div className="w-32 shrink-0">
                <p className="text-sm font-medium">{formatDay(log.log_date)}</p>
              </div>
              <span className="inline-flex w-24 items-center gap-1.5 text-sm text-ink-2">
                <Icon className="size-4 text-muted" aria-hidden />
                {mood.label}
              </span>
              <span className="tabular w-20 text-sm text-ink-2">{log.sleep_hours} sa uyku</span>
              <span className="tabular w-20 text-sm text-ink-2">Sosyal {log.social_interaction}/10</span>
              {log.meltdown && <Badge tone="warning">Kriz</Badge>}
              {log.note && <p className="min-w-0 flex-1 basis-full text-sm text-muted sm:basis-0 sm:truncate">{log.note}</p>}
              {isOwner && (
                <div className="ml-auto flex gap-1">
                  <Button variant="ghost" size="icon" aria-label="Düzenle" onClick={() => setEditing(log)}>
                    <Pencil className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Sil"
                    onClick={() => {
                      if (confirm(`${formatDay(log.log_date)} kaydı silinsin mi?`)) {
                        remove.mutate(log.id, { onSuccess: () => toast.success("Kayıt silindi") });
                      }
                    }}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {editing && (
        <DailyLogDialog
          key={editing.id}
          subjectId={subject.id}
          subjectName={subject.name}
          existing={editing}
          open
          onClose={() => setEditing(null)}
        />
      )}
    </Card>
  );
}

// --- Taramalar ------------------------------------------------------------------------

function Screenings({ subjectId }: { subjectId: number }) {
  const screenings = useScreenings(subjectId);
  if (screenings.isPending) return <Spinner />;
  if (screenings.error) return <ErrorState error={screenings.error} />;
  if (!screenings.data.length) {
    return (
      <Card>
        <EmptyState
          icon={<ClipboardList className="size-5" />}
          title="Henüz tarama yapılmadı"
          action={<ButtonLink href={`/subjects/${subjectId}/screening`}>Tarama başlat</ButtonLink>}
        />
      </Card>
    );
  }
  return (
    <Card>
      <ul className="divide-y divide-line">
        {screenings.data.map((s) => (
          <li key={s.id}>
            <Link
              href={`/subjects/${subjectId}/screenings/${s.id}`}
              className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-surface-2/60"
            >
              <span className="grid size-10 place-items-center rounded-xl bg-surface-2 text-ink-2">
                <ClipboardList className="size-5" aria-hidden />
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{INSTRUMENT_LABEL[s.instrument]}</p>
                <p className="text-sm text-muted">{formatDate(s.created_at)}</p>
              </div>
              <span className="tabular hidden text-sm text-ink-2 sm:block">
                {s.instrument === "aq10" ? `Puan ${s.score}/10` : `Model skoru ${s.score.toFixed(2)}`}
              </span>
              <RiskBadge level={s.risk_level} />
            </Link>
          </li>
        ))}
      </ul>
    </Card>
  );
}

// --- Klinik gözlemler -----------------------------------------------------------------

function Observations({ subjectId }: { subjectId: number }) {
  const observations = useObservations(subjectId);
  const [open, setOpen] = useState(false);

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setOpen(true)}>
          <Plus className="size-4" aria-hidden />
          Gözlem ekle
        </Button>
      </div>
      {observations.isPending ? (
        <Spinner />
      ) : observations.error ? (
        <ErrorState error={observations.error} />
      ) : !observations.data.length ? (
        <Card>
          <EmptyState icon={<Microscope className="size-5" />} title="Henüz klinik gözlem yok" />
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {observations.data.map((o) => (
            <Card key={o.id} className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm font-medium">{formatDate(o.created_at)}</p>
                {o.self_harm_risk !== "none" && (
                  <Badge tone={o.self_harm_risk === "high" ? "critical" : "warning"}>
                    Kendine zarar riski: {o.self_harm_risk === "high" ? "yüksek" : "düşük"}
                  </Badge>
                )}
              </div>
              <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
                {(
                  [
                    ["Göz teması", o.eye_contact],
                    ["İletişim isteği", o.communication],
                    ["Rutin uyumu", o.routine_adaptation],
                    ["Duyusal hassasiyet", o.sensory_sensitivity],
                  ] as const
                ).map(([label, value]) => (
                  <div key={label}>
                    <dt className="flex justify-between text-xs text-muted">
                      {label}
                      <span className="tabular font-medium text-ink">{value}/10</span>
                    </dt>
                    <dd className="mt-1 h-1.5 rounded-full bg-surface-2">
                      <div className="h-full rounded-full bg-[var(--series-1)]" style={{ width: `${value * 10}%` }} />
                    </dd>
                  </div>
                ))}
              </dl>
              {(o.therapy || o.eating_pattern || o.note) && (
                <div className="mt-4 space-y-1 border-t border-line pt-3 text-sm text-ink-2">
                  {o.therapy && <p>Terapi: {o.therapy}</p>}
                  {o.eating_pattern && <p>Beslenme: {o.eating_pattern}</p>}
                  {o.note && <p className="text-muted">{o.note}</p>}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
      {open && <ObservationDialog subjectId={subjectId} open onClose={() => setOpen(false)} />}
    </>
  );
}

// --- Doktor notları ---------------------------------------------------------------

function Notes({ subjectId, user }: { subjectId: number; user: User }) {
  const notes = useNotes(subjectId);
  const [open, setOpen] = useState(false);

  return (
    <>
      {user.role === "doctor" && (
        <div className="mb-4 flex justify-end">
          <Button onClick={() => setOpen(true)}>
            <Plus className="size-4" aria-hidden />
            Not ekle
          </Button>
        </div>
      )}
      {notes.isPending ? (
        <Spinner />
      ) : notes.error ? (
        <ErrorState error={notes.error} />
      ) : !notes.data.length ? (
        <Card>
          <EmptyState icon={<Stethoscope className="size-5" />} title="Henüz doktor notu yok" />
        </Card>
      ) : (
        <ol className="relative space-y-4 border-l border-line pl-6">
          {notes.data.map((note) => (
            <li key={note.id} className="relative">
              <span className="absolute top-5 -left-[29px] size-2.5 rounded-full bg-brand ring-4 ring-page" aria-hidden />
              <Card className="p-5">
                <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1">
                  <p className="font-medium">{note.doctor?.full_name ?? "Doktor"}</p>
                  <p className="text-sm text-muted">{formatDate(note.created_at)}</p>
                  {note.next_visit && (
                    <Badge tone="info" className="ml-auto">
                      <CalendarClock className="size-3.5" aria-hidden />
                      {formatDay(note.next_visit)}
                    </Badge>
                  )}
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-line">{note.body}</p>
                {note.recommendation && (
                  <div className="mt-3 rounded-xl bg-brand-soft px-3.5 py-2.5 text-sm">
                    <span className="font-medium text-brand">Öneri: </span>
                    {note.recommendation}
                  </div>
                )}
              </Card>
            </li>
          ))}
        </ol>
      )}
      {open && <NoteDialog subjectId={subjectId} open onClose={() => setOpen(false)} />}
    </>
  );
}

// --- Bakım ekibi ------------------------------------------------------------------

function Team({ subject, user }: { subject: Subject; user: User }) {
  const isOwner = subject.owner.id === user.id;
  const add = useAddDoctor(subject.id);
  const remove = useRemoveDoctor(subject.id);
  const deleteSubject = useDeleteSubject();
  const router = useRouter();
  const [email, setEmail] = useState("");

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
      <Card>
        <CardHeader
          title="Bakım ekibi"
          description="Bu listedeki doktorlar kayıtları görebilir, gözlem ve not ekleyebilir, sizinle mesajlaşabilir."
        />
        <ul className="divide-y divide-line px-5 py-2">
          {subject.care_team.length === 0 && <li className="py-6 text-center text-sm text-muted">Ekipte henüz doktor yok.</li>}
          {subject.care_team.map((d) => (
            <li key={d.id} className="flex items-center gap-3 py-3">
              <Avatar name={d.full_name} />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">{d.full_name}</p>
                <p className="truncate text-xs text-muted">{d.email}</p>
              </div>
              {(isOwner || d.id === user.id) && (
                <Button
                  variant="ghost"
                  size="sm"
                  loading={remove.isPending && remove.variables === d.id}
                  onClick={() => {
                    const self = d.id === user.id;
                    if (!confirm(self ? "Bu danışanın ekibinden ayrılmak istiyor musunuz?" : `${d.full_name} ekipten çıkarılsın mı? Erişimi hemen kalkar.`)) return;
                    remove.mutate(d.id, {
                      onSuccess: () => {
                        toast.success(self ? "Ekipten ayrıldınız" : "Doktor ekipten çıkarıldı");
                        if (self) router.push("/dashboard");
                      },
                    });
                  }}
                >
                  <X className="size-4" aria-hidden />
                  {d.id === user.id ? "Ayrıl" : "Çıkar"}
                </Button>
              )}
            </li>
          ))}
        </ul>
      </Card>

      {isOwner && (
        <div className="space-y-4">
          <Card className="p-5">
            <h2 className="flex items-center gap-2 font-semibold tracking-tight">
              <UserPlus className="size-4 text-brand" aria-hidden />
              Doktor ekle
            </h2>
            <p className="mt-1 text-sm text-muted">Doktorunuzun NeuroTrack’e kayıtlı e-posta adresini girin.</p>
            <form
              className="mt-4 space-y-3"
              onSubmit={(e) => {
                e.preventDefault();
                add.mutate(email, {
                  onSuccess: (doctor) => {
                    toast.success(`${doctor.full_name} ekibe eklendi`);
                    setEmail("");
                  },
                });
              }}
            >
              <Field label="Doktor e-postası">
                {(id) => (
                  <Input id={id} type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="doktor@klinik.com" />
                )}
              </Field>
              <Button type="submit" className="w-full" loading={add.isPending}>
                Ekibe ekle
              </Button>
            </form>
          </Card>

          {subject.kind === "child" && (
            <Card className="border-critical/30 p-5">
              <h2 className="font-semibold tracking-tight text-critical-ink">Kaydı sil</h2>
              <p className="mt-1 text-sm text-muted">
                {subject.name} ile ilgili tüm kayıtlar, taramalar ve notlar kalıcı olarak silinir.
              </p>
              <Button
                variant="danger"
                size="sm"
                className="mt-4"
                loading={deleteSubject.isPending}
                onClick={() => {
                  if (!confirm(`${subject.name} ve tüm verileri kalıcı olarak silinsin mi?`)) return;
                  deleteSubject.mutate(subject.id, {
                    onSuccess: () => {
                      toast.success("Kayıt silindi");
                      router.push("/dashboard");
                    },
                  });
                }}
              >
                <Trash2 className="size-4" aria-hidden />
                Kalıcı olarak sil
              </Button>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
