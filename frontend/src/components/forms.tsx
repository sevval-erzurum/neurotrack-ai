"use client";

import { Angry, Annoyed, Frown, Laugh, Meh, Smile, type LucideIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { cn } from "@/lib/cn";
import { MOODS, todayISO } from "@/lib/format";
import { useAddNote, useAddObservation, useCreateChild, useSaveLog } from "@/lib/queries";
import type { DailyLog, DailyLogInput, Mood, ObservationInput } from "@/lib/types";

import { Button, Dialog, Field, Input, Scale, Select, Textarea } from "./ui";

export const MOOD_ICON: Record<Mood, LucideIcon> = {
  happy: Laugh,
  calm: Smile,
  tired: Meh,
  anxious: Annoyed,
  sad: Frown,
  angry: Angry,
};

export function DailyLogDialog({
  subjectId,
  subjectName,
  open,
  onClose,
  existing,
}: {
  subjectId: number;
  subjectName: string;
  open: boolean;
  onClose: () => void;
  existing?: DailyLog;
}) {
  const save = useSaveLog(subjectId);
  const [form, setForm] = useState<DailyLogInput>(() => ({
    log_date: existing?.log_date ?? todayISO(),
    mood: existing?.mood ?? "calm",
    sleep_hours: existing?.sleep_hours ?? 8,
    social_interaction: existing?.social_interaction ?? 5,
    meltdown: existing?.meltdown ?? false,
    note: existing?.note ?? "",
  }));

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title={existing ? "Kaydı düzenle" : "Günlük kayıt"}
      description={`${subjectName} · Aynı gün için tekrar kayıt girerseniz önceki kayıt güncellenir.`}
    >
      <form
        className="space-y-5"
        onSubmit={(e) => {
          e.preventDefault();
          save.mutate(
            { ...form, note: form.note?.trim() || null },
            {
              onSuccess: () => {
                toast.success("Kayıt kaydedildi");
                onClose();
              },
            },
          );
        }}
      >
        <Field label="Tarih">
          {(id) => (
            <Input
              id={id}
              type="date"
              max={todayISO()}
              required
              value={form.log_date}
              onChange={(e) => setForm({ ...form, log_date: e.target.value })}
            />
          )}
        </Field>

        <fieldset>
          <legend className="mb-2 text-sm font-medium">Genel duygu durumu</legend>
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
            {MOODS.map((m) => {
              const Icon = MOOD_ICON[m.value];
              const selected = form.mood === m.value;
              return (
                <label
                  key={m.value}
                  className={cn(
                    "flex cursor-pointer flex-col items-center gap-1 rounded-xl border py-2.5 text-xs transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-focus",
                    selected ? "border-brand bg-brand-soft font-medium text-ink" : "border-line-strong text-ink-2 hover:bg-surface-2",
                  )}
                >
                  <input
                    type="radio"
                    name="mood"
                    className="sr-only"
                    checked={selected}
                    onChange={() => setForm({ ...form, mood: m.value })}
                  />
                  <Icon className={cn("size-5", selected ? "text-brand" : "text-muted")} aria-hidden />
                  {m.label}
                </label>
              );
            })}
          </div>
        </fieldset>

        <Scale
          label="Uyku süresi"
          unit=" saat"
          min={0}
          max={14}
          step={0.5}
          value={form.sleep_hours}
          onChange={(v) => setForm({ ...form, sleep_hours: v })}
        />
        <Scale
          label="Sosyal etkileşim"
          unit="/10"
          value={form.social_interaction}
          onChange={(v) => setForm({ ...form, social_interaction: v })}
          lowLabel="Hiç"
          highLabel="Çok yoğun"
        />

        <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-line-strong p-3.5">
          <input
            type="checkbox"
            checked={form.meltdown}
            onChange={(e) => setForm({ ...form, meltdown: e.target.checked })}
            className="mt-0.5 size-4 accent-[var(--brand)]"
          />
          <span>
            <span className="block text-sm font-medium">Bugün kriz (meltdown) yaşandı</span>
            <span className="block text-xs text-muted">Uyarılar son 7 günde 2 ve üzeri krizde tetiklenir.</span>
          </span>
        </label>

        <Field label="Not (isteğe bağlı)">
          {(id) => (
            <Textarea
              id={id}
              maxLength={2000}
              placeholder="Tetikleyiciler, iyi giden şeyler, dikkat çeken davranışlar…"
              value={form.note ?? ""}
              onChange={(e) => setForm({ ...form, note: e.target.value })}
            />
          )}
        </Field>

        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="secondary" onClick={onClose}>
            Vazgeç
          </Button>
          <Button type="submit" loading={save.isPending}>
            Kaydet
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

export function AddChildDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const create = useCreateChild();
  const [form, setForm] = useState({ name: "", birth_date: "", sex: "" });

  return (
    <Dialog open={open} onClose={onClose} title="Çocuk ekle" description="Q-CHAT taraması 18–24 aylık çocuklar için kullanılabilir.">
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          create.mutate(
            { name: form.name, birth_date: form.birth_date, sex: form.sex || null },
            {
              onSuccess: () => {
                toast.success(`${form.name} eklendi`);
                setForm({ name: "", birth_date: "", sex: "" });
                onClose();
              },
            },
          );
        }}
      >
        <Field label="Ad">
          {(id) => (
            <Input id={id} required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          )}
        </Field>
        <Field label="Doğum tarihi">
          {(id) => (
            <Input
              id={id}
              type="date"
              required
              max={todayISO()}
              value={form.birth_date}
              onChange={(e) => setForm({ ...form, birth_date: e.target.value })}
            />
          )}
        </Field>
        <Field label="Cinsiyet (isteğe bağlı)">
          {(id) => (
            <Select id={id} value={form.sex} onChange={(e) => setForm({ ...form, sex: e.target.value })}>
              <option value="">Belirtmek istemiyorum</option>
              <option value="female">Kız</option>
              <option value="male">Erkek</option>
              <option value="other">Diğer</option>
            </Select>
          )}
        </Field>
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="secondary" onClick={onClose}>
            Vazgeç
          </Button>
          <Button type="submit" loading={create.isPending}>
            Ekle
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

const OBSERVATION_SCALES: { key: keyof ObservationInput; label: string; low: string; high: string }[] = [
  { key: "eye_contact", label: "Göz teması", low: "Çok az", high: "Doğal" },
  { key: "communication", label: "İletişim isteği", low: "Çok az", high: "Yüksek" },
  { key: "routine_adaptation", label: "Rutin değişikliğine uyum", low: "Çok zor", high: "Kolay" },
  { key: "sensory_sensitivity", label: "Duyusal hassasiyet", low: "Yok", high: "Çok yüksek" },
];

export function ObservationDialog({ subjectId, open, onClose }: { subjectId: number; open: boolean; onClose: () => void }) {
  const add = useAddObservation(subjectId);
  const [form, setForm] = useState<ObservationInput>({
    sensory_sensitivity: 5,
    eye_contact: 5,
    communication: 5,
    routine_adaptation: 5,
    eating_pattern: "",
    therapy: "",
    self_harm_risk: "none",
    note: "",
  });

  return (
    <Dialog open={open} onClose={onClose} title="Klinik gözlem" description="Haftalık ya da görüşme sonrası yapılandırılmış gözlem.">
      <form
        className="space-y-5"
        onSubmit={(e) => {
          e.preventDefault();
          add.mutate(
            {
              ...form,
              eating_pattern: form.eating_pattern?.trim() || null,
              therapy: form.therapy?.trim() || null,
              note: form.note?.trim() || null,
            },
            {
              onSuccess: () => {
                toast.success("Gözlem kaydedildi");
                onClose();
              },
            },
          );
        }}
      >
        {OBSERVATION_SCALES.map((s) => (
          <Scale
            key={s.key}
            label={s.label}
            unit="/10"
            lowLabel={s.low}
            highLabel={s.high}
            value={form[s.key] as number}
            onChange={(v) => setForm({ ...form, [s.key]: v })}
          />
        ))}
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Beslenme düzeni">
            {(id) => (
              <Input id={id} value={form.eating_pattern ?? ""} onChange={(e) => setForm({ ...form, eating_pattern: e.target.value })} />
            )}
          </Field>
          <Field label="Terapi / ilaç">
            {(id) => <Input id={id} value={form.therapy ?? ""} onChange={(e) => setForm({ ...form, therapy: e.target.value })} />}
          </Field>
        </div>
        <Field label="Kendine zarar riski" hint="Yüksek seçilirse bakım ekibine acil bildirim gider.">
          {(id) => (
            <Select
              id={id}
              value={form.self_harm_risk}
              onChange={(e) => setForm({ ...form, self_harm_risk: e.target.value as ObservationInput["self_harm_risk"] })}
            >
              <option value="none">Yok</option>
              <option value="low">Düşük</option>
              <option value="high">Yüksek</option>
            </Select>
          )}
        </Field>
        <Field label="Not">
          {(id) => <Textarea id={id} value={form.note ?? ""} onChange={(e) => setForm({ ...form, note: e.target.value })} />}
        </Field>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Vazgeç
          </Button>
          <Button type="submit" loading={add.isPending}>
            Kaydet
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

export function NoteDialog({ subjectId, open, onClose }: { subjectId: number; open: boolean; onClose: () => void }) {
  const add = useAddNote(subjectId);
  const [form, setForm] = useState({ body: "", recommendation: "", next_visit: "" });

  return (
    <Dialog open={open} onClose={onClose} title="Doktor notu" description="Not, ebeveyn/danışan tarafından görülür ve bildirim gönderilir.">
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          add.mutate(
            { body: form.body, recommendation: form.recommendation.trim() || null, next_visit: form.next_visit || null },
            {
              onSuccess: () => {
                toast.success("Not eklendi");
                setForm({ body: "", recommendation: "", next_visit: "" });
                onClose();
              },
            },
          );
        }}
      >
        <Field label="Değerlendirme">
          {(id) => (
            <Textarea id={id} required rows={5} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
          )}
        </Field>
        <Field label="Öneri">
          {(id) => (
            <Textarea
              id={id}
              rows={3}
              value={form.recommendation}
              onChange={(e) => setForm({ ...form, recommendation: e.target.value })}
            />
          )}
        </Field>
        <Field label="Sonraki görüşme">
          {(id) => (
            <Input
              id={id}
              type="date"
              min={todayISO()}
              value={form.next_visit}
              onChange={(e) => setForm({ ...form, next_visit: e.target.value })}
            />
          )}
        </Field>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Vazgeç
          </Button>
          <Button type="submit" loading={add.isPending}>
            Notu ekle
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
