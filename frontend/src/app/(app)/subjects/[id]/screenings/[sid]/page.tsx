"use client";

import { ArrowLeft, BrainCircuit, CheckCircle2, Info, MessageSquare, Stethoscope } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { ContributionChart, ThresholdMeter } from "@/components/charts";
import { ButtonLink, Card, CardHeader, ErrorState, PageHeader, RiskBadge, Spinner } from "@/components/ui";
import { INSTRUMENT_LABEL, formatDate } from "@/lib/format";
import { useInstruments, useScreening, useSubject } from "@/lib/queries";
import type { Instruments, Screening, Subject } from "@/lib/types";

const HEADLINE = {
  low: {
    title: "Uzman değerlendirmesi şu an önerilmiyor",
    text: "Yanıtlar, tarama eşiğinin altında. Gelişimi izlemeye ve endişeniz olursa doktorunuzla konuşmaya devam edin.",
  },
  elevated: {
    title: "Uzman değerlendirmesi öneriliyor",
    text: "Yanıtlar tarama eşiğinin üzerinde. Bu bir tanı değildir; bir çocuk psikiyatristi veya gelişim uzmanıyla görüşmeniz önerilir.",
  },
  high: {
    title: "Uzman değerlendirmesi güçlü biçimde öneriliyor",
    text: "Yanıtlar eşiğin belirgin biçimde üzerinde. Bu bir tanı değildir; en kısa sürede bir uzmandan randevu almanız önerilir.",
  },
};

export default function ScreeningResultPage() {
  const params = useParams<{ id: string; sid: string }>();
  const subjectId = Number(params.id);
  const screening = useScreening(subjectId, Number(params.sid));
  const subject = useSubject(subjectId);
  const instruments = useInstruments();

  if (screening.isPending || subject.isPending || instruments.isPending) return <Spinner />;
  if (screening.error || subject.error || instruments.error) {
    return <ErrorState error={screening.error ?? subject.error ?? instruments.error} />;
  }

  const s = screening.data;
  const headline = HEADLINE[s.risk_level];

  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader
        eyebrow={
          <Link href={`/subjects/${subjectId}?tab=screenings`} className="inline-flex items-center gap-1.5 hover:text-ink">
            <ArrowLeft className="size-4" aria-hidden />
            {subject.data.name} · taramalar
          </Link>
        }
        title={`${INSTRUMENT_LABEL[s.instrument]} sonucu`}
        description={formatDate(s.created_at)}
      />

      <Card className="mb-4 overflow-hidden">
        <div className="flex flex-col gap-6 p-6 sm:flex-row sm:items-center">
          <div className="flex-1">
            <RiskBadge level={s.risk_level} />
            <h2 className="mt-3 text-xl font-semibold tracking-tight">{headline.title}</h2>
            <p className="mt-1.5 text-[15px] leading-relaxed text-ink-2">{headline.text}</p>
          </div>
          <div className="w-full sm:w-72">
            {s.instrument === "qchat10" ? (
              <>
                <p className="text-sm text-muted">Model skoru</p>
                <p className="tabular mb-3 text-3xl font-semibold tracking-tight">{s.score.toFixed(2)}</p>
                <ThresholdMeter value={s.score} threshold={s.details.threshold ?? 0.5} />
              </>
            ) : (
              <>
                <p className="text-sm text-muted">AQ-10 puanı</p>
                <p className="tabular text-3xl font-semibold tracking-tight">
                  {s.score} <span className="text-lg font-normal text-muted">/ 10</span>
                </p>
                <p className="mt-1 text-sm text-ink-2">Yönlendirme eşiği: {s.details.threshold ?? 6} ve üzeri</p>
              </>
            )}
          </div>
        </div>
        <NextSteps subject={subject.data} />
      </Card>

      {s.instrument === "qchat10" ? (
        <QchatExplanation screening={s} instruments={instruments.data} />
      ) : (
        <Aq10Explanation screening={s} instruments={instruments.data} />
      )}
    </div>
  );
}

function NextSteps({ subject }: { subject: Subject }) {
  const doctor = subject.care_team[0];
  return (
    <div className="flex flex-wrap items-center gap-3 border-t border-line bg-surface-2/50 px-6 py-4">
      <Stethoscope className="size-4 text-muted" aria-hidden />
      {doctor ? (
        <>
          <p className="flex-1 text-sm text-ink-2">
            Sonuç bakım ekibinizdeki <b>{doctor.full_name}</b> tarafından görülebilir.
          </p>
          <ButtonLink size="sm" variant="secondary" href={`/messages?with=${doctor.id}`}>
            <MessageSquare className="size-4" aria-hidden />
            Doktora yaz
          </ButtonLink>
        </>
      ) : (
        <>
          <p className="flex-1 text-sm text-ink-2">Sonucu bir uzmanla paylaşmak için doktorunuzu bakım ekibine ekleyin.</p>
          <ButtonLink size="sm" variant="secondary" href={`/subjects/${subject.id}?tab=team`}>
            Doktor ekle
          </ButtonLink>
        </>
      )}
    </div>
  );
}

function QchatExplanation({ screening, instruments }: { screening: Screening; instruments: Instruments }) {
  const items = new Map(instruments.qchat10.items.map((it) => [it.item, it]));
  const contributions = screening.details.contributions ?? [];
  const model = instruments.qchat10.model;

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
      <Card>
        <CardHeader
          title="Sonucu hangi yanıtlar etkiledi?"
          description="Her madde, yanıtın ortalama bir çocuğa göre skoru ne kadar değiştirdiğini gösterir."
        />
        <div className="p-5 pt-5">
          <ContributionChart
            contributions={contributions}
            optionLabel={(item, answer) => items.get(item)?.options[answer] ?? `Yanıt ${answer}`}
          />
          <p className="mt-5 text-xs leading-relaxed text-muted">
            Katkılar, lojistik regresyon modelinin log-odds ölçeğindedir ve toplamları model çıktısını birebir verir. Bazı
            tekrarlayıcı davranış maddeleri bu yaşta tipik gelişimde de yaygın olduğu için riski azaltan yönde
            görünebilir; bu, modelin veriden öğrendiği bir örüntüdür.
          </p>
        </div>
      </Card>

      <div className="space-y-4">
        <Card className="p-5">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <BrainCircuit className="size-4 text-brand" aria-hidden />
            Model hakkında
          </h3>
          <dl className="mt-3 space-y-2 text-sm">
            <Row label="Model" value={model.label} />
            <Row label="Duyarlılık" value={`%${Math.round(model.sensitivity * 100)}`} />
            <Row label="Özgüllük" value={`%${Math.round(model.specificity * 100)}`} />
            <Row label="Sürüm" value={screening.details.model_version ?? model.version} />
          </dl>
          <Link href="/model" className="mt-4 inline-block text-sm font-medium text-brand hover:underline">
            Model kartını incele →
          </Link>
        </Card>
        <Card className="p-5">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Info className="size-4 text-info-ink" aria-hidden />
            Bu skoru nasıl okumalı?
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-ink-2">
            Model skoru bir olasılık değildir: model, yarısından fazlası otizm tanılı çocuklardan oluşan bir örneklemle
            eğitildi. Önemli olan skorun eşiğin hangi tarafında olduğudur. Eşik, otizmli çocukların %90’ını yakalayacak
            şekilde seçildi.
          </p>
        </Card>
      </div>
    </div>
  );
}

function Aq10Explanation({ screening, instruments }: { screening: Screening; instruments: Instruments }) {
  const scored = new Set(screening.details.scored_items ?? []);
  return (
    <Card>
      <CardHeader
        title="Puan alan maddeler"
        description="AQ-10, her maddede otizmle ilişkili yöndeki yanıta 1 puan verir. Kural tabanlıdır; makine öğrenmesi kullanılmaz."
      />
      <ol className="divide-y divide-line px-5 py-2">
        {instruments.aq10.items.map((it) => {
          const answer = screening.answers[String(it.item)];
          return (
            <li key={it.item} className="flex items-start gap-3 py-3">
              {scored.has(it.item) ? (
                <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-warning-ink" aria-label="Puan aldı" />
              ) : (
                <span className="mt-0.5 size-4 shrink-0 rounded-full border border-line-strong" aria-label="Puan almadı" />
              )}
              <div className="min-w-0 flex-1">
                <p className="text-sm">{it.question}</p>
                <p className="text-xs text-muted">{it.options[answer]}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </Card>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-muted">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}
