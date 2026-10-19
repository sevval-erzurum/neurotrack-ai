"use client";

import { ArrowLeft, ArrowRight, Check, ClipboardList, Info } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import { Button, ButtonLink, Card, EmptyState, ErrorState, PageHeader, Spinner } from "@/components/ui";
import { cn } from "@/lib/cn";
import { formatAge } from "@/lib/format";
import { useInstruments, useRunScreening, useSubject } from "@/lib/queries";
import type { Instrument, InstrumentItem } from "@/lib/types";

export default function ScreeningPage() {
  const id = Number(useParams<{ id: string }>().id);
  const subject = useSubject(id);
  const instruments = useInstruments();

  if (subject.isPending || instruments.isPending) return <Spinner />;
  if (subject.error || instruments.error) return <ErrorState error={subject.error ?? instruments.error} />;

  const s = subject.data;
  const back = (
    <ButtonLink variant="secondary" href={`/subjects/${id}`}>
      Geri dön
    </ButtonLink>
  );

  if (s.kind === "child") {
    const [lo, hi] = instruments.data.qchat10.age_range_months;
    const age = s.age_months;
    if (age === null || age < lo || age > hi) {
      return (
        <Card>
          <EmptyState
            icon={<Info className="size-5" />}
            title="Bu yaş için uygun bir tarama yok"
            description={`Q-CHAT modeli ${lo}–${hi} aylık çocuklarla eğitildi; ${s.name} şu an ${formatAge(age)}. Bu yaş aralığı dışında sonuç güvenilir olmaz. Endişeleriniz varsa doğrudan bir uzmana başvurun.`}
            action={back}
          />
        </Card>
      );
    }
    return <Questionnaire subjectId={id} subjectName={s.name} instrument="qchat10" meta={instruments.data.qchat10} />;
  }
  return <Questionnaire subjectId={id} subjectName="Kendi değerlendirmeniz" instrument="aq10" meta={instruments.data.aq10} />;
}

function Questionnaire({
  subjectId,
  subjectName,
  instrument,
  meta,
}: {
  subjectId: number;
  subjectName: string;
  instrument: Instrument;
  meta: { name: string; description: string; items: InstrumentItem[] };
}) {
  const router = useRouter();
  const run = useRunScreening(subjectId);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [step, setStep] = useState(-1);
  const items = meta.items;
  const total = items.length;
  const answered = Object.keys(answers).length;
  const current = items[step];

  const choose = (value: number) => {
    setAnswers((a) => ({ ...a, [current.item]: value }));
    // Seçimden sonra kısa bir gecikmeyle ilerle; kullanıcı seçimini görebilsin.
    setTimeout(() => setStep((s) => Math.min(s + 1, total)), 180);
  };

  const submit = () =>
    run.mutate({ instrument, answers }, { onSuccess: (result) => router.replace(`/subjects/${subjectId}/screenings/${result.id}`) });

  if (step === -1) {
    return (
      <div className="mx-auto max-w-2xl">
        <PageHeader eyebrow={subjectName} title={meta.name} description={meta.description} />
        <Card className="space-y-4 p-6">
          <ul className="space-y-3 text-sm text-ink-2">
            <li className="flex gap-3">
              <Check className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
              {total} soru, yaklaşık {Math.ceil(total / 4)} dakika.
            </li>
            <li className="flex gap-3">
              <Check className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
              {instrument === "qchat10"
                ? "Çocuğunuzun son birkaç aydaki tipik davranışını düşünerek yanıtlayın."
                : "Kendinizi en iyi tanımlayan seçeneği işaretleyin; doğru ya da yanlış yanıt yok."}
            </li>
            <li className="flex gap-3">
              <Info className="mt-0.5 size-4 shrink-0 text-info-ink" aria-hidden />
              Sonuç tanı değildir; yalnızca uzman değerlendirmesinin önerilip önerilmediğini gösterir.
            </li>
          </ul>
          <div className="flex justify-between pt-2">
            <ButtonLink variant="ghost" href={`/subjects/${subjectId}`}>
              Vazgeç
            </ButtonLink>
            <Button onClick={() => setStep(0)}>
              Başla
              <ArrowRight className="size-4" aria-hidden />
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (step >= total) {
    return (
      <div className="mx-auto max-w-2xl">
        <PageHeader eyebrow={subjectName} title="Yanıtları gözden geçirin" description="Bir yanıtı değiştirmek için üzerine tıklayın." />
        <Card>
          <ol className="divide-y divide-line">
            {items.map((it, index) => (
              <li key={it.item}>
                <button
                  onClick={() => setStep(index)}
                  className="flex w-full items-start gap-3 px-5 py-3 text-left transition-colors hover:bg-surface-2/60"
                >
                  <span className="tabular w-5 shrink-0 text-sm text-muted">{index + 1}.</span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm">{it.question}</span>
                    <span className="mt-0.5 block text-sm font-medium text-brand">
                      {answers[it.item] !== undefined ? it.options[answers[it.item]] : "Yanıtlanmadı"}
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ol>
        </Card>
        <div className="mt-4 flex justify-between">
          <Button variant="secondary" onClick={() => setStep(total - 1)}>
            <ArrowLeft className="size-4" aria-hidden />
            Geri
          </Button>
          <Button onClick={submit} loading={run.isPending} disabled={answered < total}>
            <ClipboardList className="size-4" aria-hidden />
            Sonucu hesapla
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6">
        <div className="mb-2 flex justify-between text-sm text-muted">
          <span>{meta.name}</span>
          <span className="tabular">
            {step + 1} / {total}
          </span>
        </div>
        <div
          className="h-1.5 overflow-hidden rounded-full bg-surface-2"
          role="progressbar"
          aria-valuenow={step + 1}
          aria-valuemin={1}
          aria-valuemax={total}
          aria-label="İlerleme"
        >
          <div className="h-full rounded-full bg-brand transition-[width] duration-300" style={{ width: `${((step + 1) / total) * 100}%` }} />
        </div>
      </div>

      <Card className="p-6 sm:p-8">
        <fieldset key={current.item}>
          <legend className="text-xl font-semibold leading-snug tracking-tight">{current.question}</legend>
          <div className="mt-6 space-y-2">
            {current.options.map((option, value) => {
              const selected = answers[current.item] === value;
              return (
                <label
                  key={option}
                  className={cn(
                    "flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3.5 transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-focus",
                    selected ? "border-brand bg-brand-soft" : "border-line-strong hover:bg-surface-2",
                  )}
                >
                  <input
                    type="radio"
                    name={`item-${current.item}`}
                    className="sr-only"
                    checked={selected}
                    onChange={() => choose(value)}
                    autoFocus={value === 0}
                  />
                  <span
                    className={cn(
                      "grid size-5 shrink-0 place-items-center rounded-full border-2",
                      selected ? "border-brand bg-brand" : "border-line-strong",
                    )}
                    aria-hidden
                  >
                    {selected && <span className="size-2 rounded-full bg-brand-ink" />}
                  </span>
                  <span className={cn("text-[15px]", selected && "font-medium")}>{option}</span>
                </label>
              );
            })}
          </div>
        </fieldset>
      </Card>

      <div className="mt-4 flex justify-between">
        <Button variant="ghost" onClick={() => setStep((s) => s - 1)}>
          <ArrowLeft className="size-4" aria-hidden />
          {step === 0 ? "Giriş" : "Önceki"}
        </Button>
        <Button
          variant="secondary"
          onClick={() => setStep((s) => s + 1)}
          disabled={answers[current.item] === undefined}
        >
          Sonraki
          <ArrowRight className="size-4" aria-hidden />
        </Button>
      </div>
      <p className="mt-6 text-center text-xs text-muted">
        <Link href={`/subjects/${subjectId}`} className="hover:underline">
          Taramadan çık
        </Link>{" "}
        · yanıtlar kaydedilmez
      </p>
    </div>
  );
}
