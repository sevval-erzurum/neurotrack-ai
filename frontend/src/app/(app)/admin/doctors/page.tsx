"use client";

import { Ban, Building2, CheckCircle2, ClipboardCheck, IdCard, RotateCcw, Users, XCircle } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { AdminOnly, DoctorStatusBadge } from "@/components/admin";
import { Button, Card, Dialog, EmptyState, ErrorState, Field, PageHeader, Skeleton, Textarea } from "@/components/ui";
import { cn } from "@/lib/cn";
import { formatDate, formatRelative } from "@/lib/format";
import { useDoctorApplications, useMe, useReviewDoctor, type ReviewAction } from "@/lib/queries";
import type { DoctorApplication, DoctorStatus } from "@/lib/types";

const FILTERS: { key: DoctorStatus | "all"; label: string }[] = [
  { key: "pending", label: "Bekleyenler" },
  { key: "approved", label: "Onaylı" },
  { key: "suspended", label: "Askıda" },
  { key: "rejected", label: "Reddedilen" },
  { key: "all", label: "Tümü" },
];

const REASON_DIALOG: Record<Exclude<ReviewAction, "approve">, { title: string; description: string; cta: string }> = {
  reject: {
    title: "Başvuruyu reddet",
    description: "Gerekçe doktora gösterilir. Reddedilen hesap hiçbir bakım ekibine eklenemez.",
    cta: "Reddet",
  },
  suspend: {
    title: "Hesabı askıya al",
    description: "Doktorun tüm danışan verilerine erişimi anında durur. Bakım ekibi kayıtları silinmez; yeniden onaylanırsa erişim geri gelir.",
    cta: "Askıya al",
  },
};

export default function AdminDoctorsPage() {
  const me = useMe();
  const params = useSearchParams();
  const router = useRouter();
  const filter = (FILTERS.find((f) => f.key === params.get("status"))?.key ?? "pending") as DoctorStatus | "all";
  const doctors = useDoctorApplications(filter === "all" ? undefined : filter);
  const review = useReviewDoctor();
  const [dialog, setDialog] = useState<{ doctor: DoctorApplication; action: "reject" | "suspend" } | null>(null);
  const [reason, setReason] = useState("");

  const run = (doctor: DoctorApplication, action: ReviewAction, why?: string) =>
    review.mutate(
      { id: doctor.id, action, reason: why },
      {
        onSuccess: () => {
          toast.success(
            action === "approve" ? `${doctor.full_name} onaylandı` : action === "reject" ? "Başvuru reddedildi" : "Hesap askıya alındı",
          );
          setDialog(null);
          setReason("");
        },
      },
    );

  return (
    <AdminOnly user={me.data}>
      <PageHeader
        title="Doktor onayları"
        description="Diploma tescil numarasını ve kurumu doğrulayın. Onaylanmayan doktor hiçbir danışan verisine erişemez."
      />

      <div className="-mx-4 mb-5 overflow-x-auto px-4 sm:mx-0 sm:px-0">
        <div role="tablist" aria-label="Duruma göre" className="flex min-w-max gap-1 border-b border-line">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              role="tab"
              aria-selected={filter === f.key}
              onClick={() => router.replace(`/admin/doctors?status=${f.key}`, { scroll: false })}
              className={cn(
                "-mb-px border-b-2 px-3 py-2 text-sm transition-colors",
                filter === f.key ? "border-brand font-medium text-ink" : "border-transparent text-muted hover:text-ink",
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {doctors.isPending && (
        <div className="space-y-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
      )}
      {doctors.error && <ErrorState error={doctors.error} retry={() => doctors.refetch()} />}
      {doctors.data?.length === 0 && (
        <Card>
          <EmptyState
            icon={<ClipboardCheck className="size-5" />}
            title={filter === "pending" ? "Bekleyen başvuru yok" : "Bu durumda doktor yok"}
          />
        </Card>
      )}

      <ul className="space-y-3">
        {doctors.data?.map((d) => (
          <li key={d.id}>
            <Card className="p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-semibold tracking-tight">{d.full_name}</h2>
                    <DoctorStatusBadge status={d.doctor_status} />
                  </div>
                  <p className="mt-0.5 text-sm text-muted">{d.email}</p>
                  <dl className="mt-3 grid gap-x-6 gap-y-1.5 text-sm sm:grid-cols-3">
                    <div className="flex items-center gap-2">
                      <IdCard className="size-4 text-muted" aria-hidden />
                      <dt className="sr-only">Diploma tescil no</dt>
                      <dd className="tabular">{d.license_number ?? "—"}</dd>
                    </div>
                    <div className="flex min-w-0 items-center gap-2">
                      <Building2 className="size-4 shrink-0 text-muted" aria-hidden />
                      <dt className="sr-only">Kurum</dt>
                      <dd className="truncate">{d.institution ?? "—"}</dd>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="size-4 text-muted" aria-hidden />
                      <dt className="sr-only">Danışan sayısı</dt>
                      <dd>{d.patient_count} bakım ekibi</dd>
                    </div>
                  </dl>
                  <p className="mt-2 text-xs text-muted">
                    Başvuru: {formatDate(d.created_at)}
                    {d.reviewed_at && ` · Son inceleme: ${formatRelative(d.reviewed_at)}`}
                  </p>
                  {d.status_reason && (
                    <p className="mt-2 rounded-lg bg-surface-2 px-3 py-2 text-sm">
                      <span className="font-medium">Gerekçe:</span> {d.status_reason}
                    </p>
                  )}
                </div>

                <div className="flex flex-wrap gap-2">
                  {d.doctor_status !== "approved" && (
                    <Button size="sm" loading={review.isPending && review.variables?.id === d.id && review.variables.action === "approve"} onClick={() => run(d, "approve")}>
                      {d.doctor_status === "pending" ? <CheckCircle2 className="size-4" aria-hidden /> : <RotateCcw className="size-4" aria-hidden />}
                      {d.doctor_status === "pending" ? "Onayla" : "Yeniden onayla"}
                    </Button>
                  )}
                  {d.doctor_status === "pending" && (
                    <Button size="sm" variant="secondary" onClick={() => setDialog({ doctor: d, action: "reject" })}>
                      <XCircle className="size-4" aria-hidden />
                      Reddet
                    </Button>
                  )}
                  {d.doctor_status === "approved" && (
                    <Button size="sm" variant="secondary" onClick={() => setDialog({ doctor: d, action: "suspend" })}>
                      <Ban className="size-4" aria-hidden />
                      Askıya al
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          </li>
        ))}
      </ul>

      <Dialog
        open={dialog !== null}
        onClose={() => setDialog(null)}
        title={dialog ? `${REASON_DIALOG[dialog.action].title}: ${dialog.doctor.full_name}` : ""}
        description={dialog ? REASON_DIALOG[dialog.action].description : undefined}
      >
        {dialog && (
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              run(dialog.doctor, dialog.action, reason.trim());
            }}
          >
            <Field label="Gerekçe">
              {(id) => <Textarea id={id} required minLength={3} maxLength={500} value={reason} onChange={(e) => setReason(e.target.value)} />}
            </Field>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" onClick={() => setDialog(null)}>
                Vazgeç
              </Button>
              <Button type="submit" variant="danger" loading={review.isPending}>
                {REASON_DIALOG[dialog.action].cta}
              </Button>
            </div>
          </form>
        )}
      </Dialog>
    </AdminOnly>
  );
}
