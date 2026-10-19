"use client";

import { CheckCircle2, CircleAlert, ScrollText, ShieldX } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

import { AdminOnly } from "@/components/admin";
import { Badge, Button, Card, EmptyState, ErrorState, PageHeader, Select, Skeleton } from "@/components/ui";
import { ROLE_LABEL, actionLabel, formatDate, formatTime } from "@/lib/format";
import { useAuditEvents, useMe } from "@/lib/queries";
import type { AuditFilters, AuditOutcome } from "@/lib/types";

const OUTCOMES: { value: AuditOutcome | ""; label: string }[] = [
  { value: "", label: "Tüm sonuçlar" },
  { value: "ok", label: "Başarılı" },
  { value: "denied", label: "Reddedildi" },
  { value: "error", label: "Hata" },
];

// Eylem kodlarının önekleri (backend: services/audit.py ACTIONS).
const CATEGORIES: { value: string; label: string }[] = [
  { value: "", label: "Tüm işlemler" },
  { value: "auth.", label: "Giriş / kayıt" },
  { value: "subject.", label: "Danışan kaydı" },
  { value: "log.", label: "Günlük kayıtlar" },
  { value: "screening.", label: "Taramalar" },
  { value: "note.", label: "Doktor notları" },
  { value: "observation.", label: "Klinik gözlemler" },
  { value: "care_team.", label: "Bakım ekibi" },
  { value: "message.", label: "Mesajlar" },
  { value: "admin.", label: "Yönetici işlemleri" },
];

const OUTCOME_BADGE: Record<AuditOutcome, { tone: "good" | "critical" | "warning"; icon: typeof CheckCircle2; label: string }> = {
  ok: { tone: "good", icon: CheckCircle2, label: "Başarılı" },
  denied: { tone: "critical", icon: ShieldX, label: "Reddedildi" },
  error: { tone: "warning", icon: CircleAlert, label: "Hata" },
};

export default function AuditPage() {
  const me = useMe();
  const params = useSearchParams();
  const router = useRouter();
  const outcome = (OUTCOMES.find((o) => o.value === params.get("outcome"))?.value || undefined) as AuditOutcome | undefined;
  const action = CATEGORIES.find((c) => c.value === params.get("action"))?.value || undefined;
  const filters: AuditFilters = { outcome, action };
  const events = useAuditEvents(filters);

  const setFilter = (key: "outcome" | "action", value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    router.replace(`/admin/audit${next.size ? `?${next}` : ""}`, { scroll: false });
  };

  const rows = events.data?.pages.flatMap((p) => p.items) ?? [];

  return (
    <AdminOnly user={me.data}>
      <PageHeader
        title="Erişim günlüğü"
        description="Kim, ne zaman, hangi kayıtta ne yaptı. İstek içerikleri saklanmaz; günlükte sağlık verisi bulunmaz."
      />

      <div className="mb-4 flex flex-wrap gap-2">
        <label className="sr-only" htmlFor="audit-outcome">
          Sonuç
        </label>
        <Select id="audit-outcome" className="w-auto" value={outcome ?? ""} onChange={(e) => setFilter("outcome", e.target.value)}>
          {OUTCOMES.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </Select>
        <label className="sr-only" htmlFor="audit-action">
          İşlem türü
        </label>
        <Select id="audit-action" className="w-auto" value={action ?? ""} onChange={(e) => setFilter("action", e.target.value)}>
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </Select>
      </div>

      {events.isPending && <Skeleton className="h-96" />}
      {events.error && <ErrorState error={events.error} retry={() => events.refetch()} />}
      {events.data && rows.length === 0 && (
        <Card>
          <EmptyState icon={<ScrollText className="size-5" />} title="Bu filtrelerle kayıt yok" />
        </Card>
      )}

      {rows.length > 0 && (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="border-b border-line bg-surface-2/60 text-left text-xs text-muted">
                <tr>
                  <th className="px-4 py-2.5 font-medium">Zaman</th>
                  <th className="px-4 py-2.5 font-medium">Kişi</th>
                  <th className="px-4 py-2.5 font-medium">İşlem</th>
                  <th className="px-4 py-2.5 font-medium">Kayıt</th>
                  <th className="px-4 py-2.5 font-medium">Sonuç</th>
                  <th className="px-4 py-2.5 font-medium">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {rows.map((e) => {
                  const badge = OUTCOME_BADGE[e.outcome];
                  return (
                    <tr key={e.id} className="align-top">
                      <td className="tabular whitespace-nowrap px-4 py-2.5 text-ink-2">
                        {formatDate(e.created_at)}
                        <span className="block text-xs text-muted">{formatTime(e.created_at)}</span>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="font-medium">{e.actor_label ?? "Anonim"}</span>
                        <span className="block text-xs text-muted">
                          {e.actor_role ? ROLE_LABEL[e.actor_role] : "Oturum yok"}
                          {e.actor_id !== null && ` · #${e.actor_id}`}
                        </span>
                      </td>
                      <td className="px-4 py-2.5">
                        {actionLabel(e.action)}
                        <span className="block font-mono text-[11px] text-muted">{e.action}</span>
                      </td>
                      <td className="tabular px-4 py-2.5 text-ink-2">
                        {e.subject_id !== null ? `#${e.subject_id}` : e.target_user_id !== null ? `kullanıcı #${e.target_user_id}` : "—"}
                      </td>
                      <td className="px-4 py-2.5">
                        <Badge tone={badge.tone}>
                          <badge.icon className="size-3.5" aria-hidden />
                          {badge.label}
                        </Badge>
                        <span className="tabular ml-1.5 text-xs text-muted">{e.status_code}</span>
                      </td>
                      <td className="tabular px-4 py-2.5 text-xs text-muted">{e.ip ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {events.hasNextPage && (
            <div className="border-t border-line p-3 text-center">
              <Button variant="ghost" size="sm" loading={events.isFetchingNextPage} onClick={() => events.fetchNextPage()}>
                Daha eski kayıtlar
              </Button>
            </div>
          )}
        </Card>
      )}
    </AdminOnly>
  );
}
