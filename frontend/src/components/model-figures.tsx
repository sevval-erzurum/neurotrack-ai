import { cn } from "@/lib/cn";
import type { ModelReport } from "@/lib/types";

// Model kartının düz HTML/CSS figürleri. recharts'a bağımlı değiller, bu yüzden sunucuda
// render edilirler; recharts kullanan grafikler (charts.tsx) yalnızca istemcide yüklenir.

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

