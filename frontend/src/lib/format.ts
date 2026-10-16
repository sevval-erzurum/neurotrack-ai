import type { Mood, RiskLevel, Role } from "./types";

export const MOODS: { value: Mood; label: string; valence: -1 | 0 | 1 }[] = [
  { value: "happy", label: "Mutlu", valence: 1 },
  { value: "calm", label: "Sakin", valence: 1 },
  { value: "tired", label: "Yorgun", valence: 0 },
  { value: "anxious", label: "Kaygılı", valence: -1 },
  { value: "sad", label: "Üzgün", valence: -1 },
  { value: "angry", label: "Öfkeli", valence: -1 },
];

export const moodOf = (mood: Mood) => MOODS.find((m) => m.value === mood)!;

export const ROLE_LABEL: Record<Role, string> = {
  adult: "Yetişkin",
  parent: "Ebeveyn",
  doctor: "Doktor",
};

export const RISK_LABEL: Record<RiskLevel, string> = {
  low: "Düşük",
  elevated: "Değerlendirme önerilir",
  high: "Yüksek",
};

export const INSTRUMENT_LABEL = { qchat10: "Q-CHAT-10", aq10: "AQ-10" } as const;

const dateFmt = new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "long", year: "numeric" });
const shortFmt = new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "short" });
const timeFmt = new Intl.DateTimeFormat("tr-TR", { hour: "2-digit", minute: "2-digit" });

// "YYYY-MM-DD" yerel tarih olarak yorumlanır; Date(...) UTC kabul edip bir gün kaydırabilir.
export function parseDay(day: string): Date {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function todayISO(): string {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}

export const formatDay = (day: string) => dateFmt.format(parseDay(day));
export const formatShortDay = (day: string) => shortFmt.format(parseDay(day));
export const formatDate = (iso: string) => dateFmt.format(new Date(iso));

export function formatRelative(iso: string): string {
  const date = new Date(iso);
  const minutes = Math.round((Date.now() - date.getTime()) / 60_000);
  if (minutes < 1) return "şimdi";
  if (minutes < 60) return `${minutes} dk önce`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} sa önce`;
  const days = Math.round(hours / 24);
  if (days === 1) return `dün ${timeFmt.format(date)}`;
  if (days < 7) return `${days} gün önce`;
  return shortFmt.format(date);
}

export const formatTime = (iso: string) => timeFmt.format(new Date(iso));

export function formatAge(months: number | null): string {
  if (months === null) return "—";
  if (months < 36) return `${months} aylık`;
  return `${Math.floor(months / 12)} yaş`;
}

export function initials(name: string): string {
  return name
    .replace(/^Dr\.\s*/i, "")
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toLocaleUpperCase("tr-TR") ?? "")
    .join("");
}

export const percent = (value: number, digits = 0) => `%${(value * 100).toFixed(digits)}`;
