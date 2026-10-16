"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from "recharts";

import { cn } from "@/lib/cn";
import { formatDay, formatShortDay, moodOf, parseDay, todayISO } from "@/lib/format";
import type { Contribution, Insights, ModelReport } from "@/lib/types";

const AXIS = { fontSize: 11, fill: "var(--ink-muted)" };

function ChartTooltip({ active, payload, label, unit }: TooltipContentProps<number, string> & { unit: string }) {
  if (!active || !payload?.length) return null;
  const value = payload[0].value as number;
  return (
    <div className="rounded-lg border border-line bg-surface px-3 py-2 text-xs shadow-card">
      <p className="text-muted">{formatDay(String(label))}</p>
      <p className="tabular mt-0.5 text-sm font-semibold text-ink">
        {value}
        <span className="ml-0.5 font-normal text-ink-2">{unit}</span>
      </p>
    </div>
  );
}

/** Tek seri zaman grafiği. İki farklı ölçek asla tek grafikte birleştirilmez. */
export function TrendChart({
  data,
  dataKey,
  domain,
  unit,
  reference,
  ariaLabel,
}: {
  data: Insights["series"];
  dataKey: "sleep_hours" | "social_interaction";
  domain: [number, number];
  unit: string;
  reference?: { y: number; label: string };
  ariaLabel: string;
}) {
  return (
    <div className="h-48 w-full" role="img" aria-label={ariaLabel}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -12 }}>
          <CartesianGrid vertical={false} stroke="var(--grid)" />
          <XAxis
            dataKey="date"
            tickFormatter={formatShortDay}
            tick={AXIS}
            tickLine={false}
            axisLine={{ stroke: "var(--axis)" }}
            minTickGap={28}
          />
          <YAxis domain={domain} tick={AXIS} tickLine={false} axisLine={false} width={40} allowDecimals={false} />
          {reference && (
            <ReferenceLine
              y={reference.y}
              stroke="var(--ink-muted)"
              strokeOpacity={0.6}
              label={{ value: reference.label, position: "insideTopRight", fontSize: 10, fill: "var(--ink-muted)" }}
            />
          )}
          <Tooltip
            content={(props) => <ChartTooltip {...(props as TooltipContentProps<number, string>)} unit={unit} />}
            cursor={{ stroke: "var(--axis)" }}
          />
          <Line
            type="linear"
            dataKey={dataKey}
            stroke="var(--series-1)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4.5, strokeWidth: 2, stroke: "var(--surface)" }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

const VALENCE_STYLE = {
  1: { color: "var(--pole-neg)", label: "Olumlu (mutlu, sakin)" },
  0: { color: "var(--neutral-mid)", label: "Nötr (yorgun)" },
  [-1]: { color: "var(--pole-pos)", label: "Zorlayıcı (kaygılı, üzgün, öfkeli)" },
} as const;

/** Son N günün duygu durumu: olumlu ↔ zorlayıcı iki kutuplu, nötr gri orta nokta. */
export function MoodStrip({ series, days = 30 }: { series: Insights["series"]; days?: number }) {
  const cells = useMemo(() => {
    const byDate = new Map(series.map((point) => [point.date, point]));
    const today = parseDay(todayISO());
    return Array.from({ length: days }, (_, i) => {
      const d = new Date(today);
      d.setDate(d.getDate() - (days - 1 - i));
      const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      return { date: iso, point: byDate.get(iso) };
    });
  }, [series, days]);

  return (
    <div>
      <div className="grid gap-[2px]" style={{ gridTemplateColumns: `repeat(${days}, minmax(0, 1fr))` }}>
        {cells.map(({ date, point }) => {
          const mood = point ? moodOf(point.mood) : null;
          const title = point
            ? `${formatDay(date)}: ${mood!.label}${point.meltdown ? " · kriz yaşandı" : ""}`
            : `${formatDay(date)}: kayıt yok`;
          return (
            <div key={date} className="group relative" title={title}>
              {/* Kayıt olmayan gün, nötr günle karışmasın diye tam blok değil taban çizgisi olarak çizilir. */}
              <div className="flex h-8 items-end">
                <div
                  className={cn("w-full rounded-[4px] transition-opacity group-hover:opacity-80", point ? "h-full" : "h-1")}
                  style={{ background: mood ? VALENCE_STYLE[mood.valence].color : "var(--line-strong)" }}
                />
              </div>
              {point?.meltdown && (
                <span className="absolute -bottom-2.5 left-1/2 size-1.5 -translate-x-1/2 rounded-full bg-ink" aria-hidden />
              )}
              <span className="sr-only">{title}</span>
            </div>
          );
        })}
      </div>
      <div className="mt-5 flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-ink-2">
        {([1, 0, -1] as const).map((v) => (
          <span key={v} className="inline-flex items-center gap-1.5">
            <span className="size-2.5 rounded-[3px]" style={{ background: VALENCE_STYLE[v].color }} />
            {VALENCE_STYLE[v].label}
          </span>
        ))}
        <span className="inline-flex items-center gap-1.5">
          <span className="size-1.5 rounded-full bg-ink" />
          Kriz (meltdown)
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-1 w-2.5 rounded-full bg-[var(--line-strong)]" />
          Kayıt yok
        </span>
      </div>
    </div>
  );
}

/** Madde katkıları: sağa uzayan çubuk riski artırır, sola uzayan azaltır. */
export function ContributionChart({
  contributions,
  optionLabel,
}: {
  contributions: Contribution[];
  optionLabel: (item: number, answer: number) => string;
}) {
  const max = Math.max(...contributions.map((c) => Math.abs(c.log_odds)), 0.5);
  return (
    <div>
      <div className="mb-3 grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-4 text-xs text-muted">
        <span />
        <div className="flex justify-between">
          <span className="inline-flex items-center gap-1.5">
            <span className="size-2.5 rounded-[3px] bg-[var(--pole-neg)]" />
            Riski azaltan
          </span>
          <span className="inline-flex items-center gap-1.5">
            Riski artıran
            <span className="size-2.5 rounded-[3px] bg-[var(--pole-pos)]" />
          </span>
        </div>
      </div>
      <ul className="space-y-2.5">
        {contributions.map((c) => {
          const width = (Math.abs(c.log_odds) / max) * 50;
          const positive = c.log_odds >= 0;
          return (
            <li key={c.item} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] items-center gap-4">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-ink">{c.short}</p>
                <p className="truncate text-xs text-muted">{optionLabel(c.item, c.answer)}</p>
              </div>
              <div
                className="relative h-6"
                title={`${c.short}: ${positive ? "+" : ""}${c.log_odds.toFixed(2)} log-odds`}
              >
                <div className="absolute inset-y-0 left-1/2 w-px bg-[var(--axis)]" aria-hidden />
                <div
                  className="absolute inset-y-1 rounded-[4px]"
                  style={{
                    background: positive ? "var(--pole-pos)" : "var(--pole-neg)",
                    left: positive ? "50%" : `${50 - width}%`,
                    width: `${Math.max(width, 0.8)}%`,
                  }}
                />
                <span className="sr-only">
                  {positive ? "Riski artırıyor" : "Riski azaltıyor"}, katkı {c.log_odds.toFixed(2)}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/** Olasılık göstergesi: eşik çizgisiyle birlikte, renk yerine konum ve etiket anlam taşır. */
export function ThresholdMeter({ value, threshold }: { value: number; threshold: number }) {
  return (
    <div>
      <div className="relative h-2.5 rounded-full bg-surface-2">
        <div className="absolute inset-y-0 left-0 rounded-full bg-ink" style={{ width: `${value * 100}%` }} />
        <div
          className="absolute -inset-y-1.5 w-0.5 rounded bg-critical"
          style={{ left: `${threshold * 100}%` }}
          aria-hidden
        />
      </div>
      <div className="relative mt-2 h-4 text-[11px] text-muted">
        <span className="absolute left-0">0</span>
        <span className="absolute -translate-x-1/2 font-medium text-critical-ink" style={{ left: `${threshold * 100}%` }}>
          Eşik {threshold.toFixed(2)}
        </span>
        <span className="absolute right-0">1</span>
      </div>
    </div>
  );
}

export function RocChart({ model, baselineAuc }: { model: ModelReport; baselineAuc: number }) {
  const data = model.roc_curve.fpr.map((fpr, i) => ({ fpr, tpr: model.roc_curve.tpr[i] }));
  return (
    <div className="aspect-square w-full max-w-sm" role="img" aria-label={`ROC eğrisi, AUC ${model.pooled_oof_auc}`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 18, left: 0 }}>
          <CartesianGrid stroke="var(--grid)" />
          <XAxis
            type="number"
            dataKey="fpr"
            domain={[0, 1]}
            ticks={[0, 0.25, 0.5, 0.75, 1]}
            tick={AXIS}
            tickLine={false}
            axisLine={{ stroke: "var(--axis)" }}
            label={{ value: "Yanlış pozitif oranı (1 − özgüllük)", position: "bottom", offset: 2, fontSize: 11, fill: "var(--ink-2)" }}
          />
          <YAxis
            type="number"
            domain={[0, 1]}
            ticks={[0, 0.25, 0.5, 0.75, 1]}
            tick={AXIS}
            tickLine={false}
            axisLine={false}
            width={44}
            label={{ value: "Duyarlılık", angle: -90, position: "insideLeft", offset: 10, fontSize: 11, fill: "var(--ink-2)" }}
          />
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: 1, y: 1 },
            ]}
            stroke="var(--axis)"
            ifOverflow="visible"
          />
          <Tooltip
            content={({ active, payload }) =>
              active && payload?.length ? (
                <div className="rounded-lg border border-line bg-surface px-3 py-2 text-xs shadow-card">
                  <p className="tabular">Duyarlılık {(payload[0].payload.tpr * 100).toFixed(0)}%</p>
                  <p className="tabular text-muted">YP oranı {(payload[0].payload.fpr * 100).toFixed(0)}%</p>
                </div>
              ) : null
            }
          />
          <Line
            type="stepAfter"
            dataKey="tpr"
            stroke="var(--series-1)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="sr-only">Klasik toplam skorun AUC değeri {baselineAuc}.</p>
    </div>
  );
}

export function CalibrationChart({ predicted, observed }: { predicted: number[]; observed: number[] }) {
  const data = predicted.map((p, i) => ({ p, o: observed[i] }));
  return (
    <div className="aspect-square w-full max-w-sm" role="img" aria-label="Kalibrasyon eğrisi">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 18, left: 0 }}>
          <CartesianGrid stroke="var(--grid)" />
          <XAxis
            type="number"
            dataKey="p"
            domain={[0, 1]}
            ticks={[0, 0.25, 0.5, 0.75, 1]}
            tick={AXIS}
            tickLine={false}
            axisLine={{ stroke: "var(--axis)" }}
            label={{ value: "Tahmin edilen olasılık", position: "bottom", offset: 2, fontSize: 11, fill: "var(--ink-2)" }}
          />
          <YAxis
            type="number"
            domain={[0, 1]}
            ticks={[0, 0.25, 0.5, 0.75, 1]}
            tick={AXIS}
            tickLine={false}
            axisLine={false}
            width={44}
            label={{ value: "Gözlenen oran", angle: -90, position: "insideLeft", offset: 10, fontSize: 11, fill: "var(--ink-2)" }}
          />
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: 1, y: 1 },
            ]}
            stroke="var(--axis)"
            ifOverflow="visible"
          />
          <Tooltip
            content={({ active, payload }) =>
              active && payload?.length ? (
                <div className="rounded-lg border border-line bg-surface px-3 py-2 text-xs shadow-card">
                  <p className="tabular">Tahmin {(payload[0].payload.p * 100).toFixed(0)}%</p>
                  <p className="tabular text-muted">Gözlenen {(payload[0].payload.o * 100).toFixed(0)}%</p>
                </div>
              ) : null
            }
          />
          <Line
            dataKey="o"
            stroke="var(--series-1)"
            strokeWidth={2}
            dot={{ r: 4, fill: "var(--series-1)", stroke: "var(--surface)", strokeWidth: 2 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/** Model karşılaştırması: ortalama AUC (nokta) ± 1 std (çizgi), tek eksen. */
export function AucComparison({
  models,
  baseline,
  chosen,
}: {
  models: ModelReport[];
  baseline: { mean: number; std: number };
  chosen: string;
}) {
  const rows = [
    ...models.map((m) => ({ key: m.key, label: m.label, ...m.auc })),
    { key: "baseline", label: "Toplam skor (ML yok)", ...baseline },
  ];
  const lo = 0.7;
  const hi = 1;
  const x = (v: number) => `${((Math.min(Math.max(v, lo), hi) - lo) / (hi - lo)) * 100}%`;

  return (
    <div>
      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.key} className="grid grid-cols-[minmax(0,11rem)_1fr_3.5rem] items-center gap-3 text-sm">
            <span className={cn("truncate", row.key === chosen ? "font-semibold text-ink" : "text-ink-2")}>
              {row.label}
              {row.key === chosen && <span className="sr-only"> (seçilen model)</span>}
            </span>
            <div className="relative h-5" title={`AUC ${row.mean.toFixed(3)} ± ${row.std.toFixed(3)}`}>
              <div className="absolute inset-x-0 top-1/2 h-px bg-[var(--grid)]" aria-hidden />
              <div
                className="absolute top-1/2 h-0.5 -translate-y-1/2 rounded bg-[var(--axis)]"
                style={{ left: x(row.mean - row.std), right: `calc(100% - ${x(row.mean + row.std)})` }}
              />
              <div
                className={cn(
                  "absolute top-1/2 size-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-[var(--surface)]",
                )}
                style={{ left: x(row.mean), background: row.key === "baseline" ? "var(--ink-muted)" : "var(--series-1)" }}
              />
            </div>
            <span className="tabular text-right text-ink">{row.mean.toFixed(3)}</span>
          </li>
        ))}
      </ul>
      <div className="mt-2 grid grid-cols-[minmax(0,11rem)_1fr_3.5rem] gap-3 text-[11px] text-muted">
        <span />
        <div className="flex justify-between">
          <span>0.70</span>
          <span>0.85</span>
          <span>1.00</span>
        </div>
        <span />
      </div>
    </div>
  );
}

/** Madde seçim kararlılığı: 25 dış fold'un kaçında seçildi. */
export function SelectionFrequency({ items, selected }: { items: { item: number; short: string; frequency: number }[]; selected: number[] }) {
  return (
    <ul className="space-y-1.5">
      {items.map((it) => {
        const isSelected = selected.includes(it.item);
        return (
          <li key={it.item} className="grid grid-cols-[minmax(0,12rem)_1fr_3rem] items-center gap-3 text-sm">
            <span className={cn("truncate", isSelected ? "font-medium text-ink" : "text-muted")}>
              {it.item}. {it.short}
            </span>
            <div className="h-3 rounded-[4px] bg-surface-2" title={`%${Math.round(it.frequency * 100)}`}>
              <div
                className="h-full rounded-[4px]"
                style={{
                  width: `${Math.max(it.frequency * 100, 1)}%`,
                  background: isSelected ? "var(--series-1)" : "var(--axis)",
                }}
              />
            </div>
            <span className="tabular text-right text-xs text-ink-2">%{Math.round(it.frequency * 100)}</span>
          </li>
        );
      })}
    </ul>
  );
}

