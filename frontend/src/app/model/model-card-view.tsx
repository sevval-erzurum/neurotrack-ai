"use client";

import { AlertTriangle, Database, FlaskConical, Scale, Target } from "lucide-react";
import dynamic from "next/dynamic";

import { AucComparison, SelectionFrequency } from "@/components/model-figures";
import { Badge, Card, CardHeader, PageHeader, Skeleton } from "@/components/ui";
import { formatDay } from "@/lib/format";
import type { ModelCard } from "@/lib/types";

// recharts grafikleri yalnızca istemcide, hydration'dan sonra yüklenir. recharts sayfanın ilk
// istemci paketinde olduğunda Next 16.4 + React 19.2'de kök aralıklı olarak yeniden hydrate
// ediliyor ve <head> ile eşleşme bozuluyordu (React #418). ResponsiveContainer sunucuda zaten
// boyut ölçemediği için grafiklerin SSR'ı bir şey kazandırmıyordu.
const chartPlaceholder = () => <Skeleton className="aspect-square w-full max-w-sm" />;
const RocChart = dynamic(() => import("@/components/charts").then((m) => m.RocChart), {
  ssr: false,
  loading: chartPlaceholder,
});
const CalibrationChart = dynamic(() => import("@/components/charts").then((m) => m.CalibrationChart), {
  ssr: false,
  loading: chartPlaceholder,
});

export function ModelCardView({ card: m }: { card: ModelCard }) {
  const chosen = m.models.find((r) => r.key === m.chosen_model)!;
  const candidates = m.models.filter((r) => r.key !== "logreg_25");
  const reference = m.models.find((r) => r.key === "logreg_25");
  const selected = m.items.map((it) => it.item);
  const op = m.operating_point;

  return (
    <>
      <PageHeader
        eyebrow={
          <span className="flex flex-wrap items-center gap-2">
            <Badge tone="brand">{m.model_version}</Badge>
            <span>Eğitim: {formatDay(m.trained_on)}</span>
          </span>
        }
        title="Model kartı: Q-CHAT kısa form küçük çocuk taraması"
        description="Modelin nasıl değerlendirildiği, neden bu modelin seçildiği ve nerede yanılabileceği."
      />

      <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Metric icon={Target} label="AUC (nested CV)" value={chosen.auc.mean.toFixed(3)} sub={`± ${chosen.auc.std.toFixed(3)} · 25 dış fold`} />
        <Metric icon={Scale} label="Duyarlılık" value={`%${Math.round(op.sensitivity * 100)}`} sub={`Eşik ${op.threshold.toFixed(2)}`} />
        <Metric icon={Scale} label="Özgüllük" value={`%${Math.round(op.specificity * 100)}`} sub="Aynı eşikte" />
        <Metric
          icon={FlaskConical}
          label="Klasik toplam skora göre"
          value={`+${(chosen.auc.mean - m.baseline_total_score.auc.mean).toFixed(3)}`}
          sub={`Daha iyi olduğu fold oranı: %${Math.round(chosen.folds_beating_baseline * 100)}`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader
            title="Model karşılaştırması"
            description="Ortalama AUC ve ±1 standart sapma. Fark gürültü düzeyinde olduğu için en basit model seçildi."
          />
          <div className="p-5 pt-5">
            <AucComparison models={candidates} baseline={m.baseline_total_score.auc} chosen={m.chosen_model} />
            <p className="mt-5 rounded-xl bg-surface-2 px-3.5 py-3 text-sm text-ink-2">
              <b className="text-ink">Seçim kuralı:</b> {m.selection_rule}. Seçilen: <b className="text-ink">{m.chosen_model_label}</b>{" "}
              (C = {String(m.hyperparameters.C)}).
              {reference && (
                <>
                  {" "}
                  25 maddenin tamamıyla AUC {reference.auc.mean.toFixed(3)}; kısa form{" "}
                  {(reference.auc.mean - chosen.auc.mean).toFixed(3)} kaybettiriyor.
                </>
              )}
            </p>
          </div>
        </Card>

        <Card>
          <CardHeader
            title="ROC eğrisi"
            description={`Dış fold tahminleri · AUC ${chosen.pooled_oof_auc.toFixed(3)} (%95 GA ${chosen.pooled_oof_auc_ci95[0].toFixed(2)}–${chosen.pooled_oof_auc_ci95[1].toFixed(2)})`}
          />
          <div className="flex justify-center p-5 pt-3">
            <RocChart model={chosen} baselineAuc={m.baseline_total_score.pooled_auc} />
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Kalibrasyon"
            description={`Brier skoru ${chosen.brier.mean.toFixed(3)}. Köşegene yakınlık, tahmin edilen ile gözlenen oranın uyumunu gösterir.`}
          />
          <div className="flex justify-center p-5 pt-3">
            <CalibrationChart predicted={m.calibration.prob_pred} observed={m.calibration.prob_true} />
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Madde seçim kararlılığı"
            description="25 maddeden 10’u her dış fold’da yeniden seçildi (RFE). Mavi: uygulamada sorulan maddeler."
          />
          <div className="p-5 pt-4">
            <SelectionFrequency items={m.item_selection_frequency.slice(0, 16)} selected={selected} />
          </div>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Card className="p-5">
          <h2 className="flex items-center gap-2 font-semibold">
            <Database className="size-4 text-brand" aria-hidden />
            Veri
          </h2>
          <dl className="mt-3 space-y-2 text-sm">
            <Row label="Kohort" value={m.dataset.name} />
            <Row label="Örneklem" value={`${m.dataset.n} (${m.dataset.n_asd} otizm, ${m.dataset.n_control} kontrol)`} />
            <Row label="Etiket" value={m.dataset.label_source} />
          </dl>
          <a href={m.dataset.source} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sm text-brand hover:underline">
            Veri kaynağı (Mendeley Data) →
          </a>
        </Card>
        <Card className="p-5">
          <h2 className="flex items-center gap-2 font-semibold">
            <FlaskConical className="size-4 text-brand" aria-hidden />
            Değerlendirme
          </h2>
          <ul className="mt-3 space-y-2 text-sm text-ink-2">
            <li>Dış döngü: {m.evaluation.outer_cv}</li>
            <li>İç döngü: {m.evaluation.inner_cv}</li>
            <li>{m.evaluation.threshold_note}</li>
          </ul>
        </Card>
        <Card className="border-warning/40 p-5">
          <h2 className="flex items-center gap-2 font-semibold">
            <AlertTriangle className="size-4 text-warning-ink" aria-hidden />
            Sınırlılıklar
          </h2>
          <ul className="mt-3 list-disc space-y-1.5 pl-4 text-sm text-ink-2">
            <li>Örneklemin %54’ü otizm tanılı; skorlar popülasyon riski değildir.</li>
            <li>Tek ülke, 252 çocuk; dış doğrulama yapılmadı.</li>
            <li>Türkçe soru metinleri doğrulanmış bir uyarlama değildir.</li>
            <li>Tanı aracı değildir; yalnızca yönlendirme amaçlıdır.</li>
          </ul>
        </Card>
      </div>

      <Card className="mt-4 p-5">
        <h2 className="font-semibold">Neden yetişkin ve okul çağı için ML modeli yok?</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink-2">
          Yaygın kullanılan UCI otizm tarama veri setlerinde etiket, 10 sorunun toplamından deterministik olarak türetilmiştir
          (toplam &gt; 6). Bu veriyle eğitilen her model %100’e yakın doğruluk gösterir, ama öğrendiği şey otizm değil bir
          toplama işlemidir. Bu nedenle yetişkin taraması AQ-10’un yayımlanmış puanlama kuralıyla yapılır; makine öğrenmesi
          yalnızca etiketi anket puanından bağımsız, gerçek tanıdan gelen Q-CHAT verisinde kullanılır.
        </p>
      </Card>
    </>
  );
}

function Metric({ icon: Icon, label, value, sub }: { icon: typeof Target; label: string; value: string; sub: string }) {
  return (
    <Card className="p-4">
      <p className="flex items-center gap-1.5 text-sm text-muted">
        <Icon className="size-4" aria-hidden />
        {label}
      </p>
      <p className="tabular mt-1.5 text-2xl font-semibold tracking-tight">{value}</p>
      <p className="mt-0.5 text-xs text-muted">{sub}</p>
    </Card>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}
