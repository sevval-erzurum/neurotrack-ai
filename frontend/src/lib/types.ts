export type Role = "adult" | "parent" | "doctor";
export type Mood = "happy" | "calm" | "tired" | "anxious" | "sad" | "angry";
export type RiskLevel = "low" | "elevated" | "high";
export type Instrument = "qchat10" | "aq10";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
}

export interface UserBrief {
  id: number;
  full_name: string;
  role: Role;
}

export interface Doctor {
  id: number;
  full_name: string;
  email: string;
}

export interface Summary {
  latest_risk: RiskLevel | null;
  last_log_date: string | null;
  alert_count: number;
  next_visit: string | null;
}

export interface Subject {
  id: number;
  kind: "self" | "child";
  name: string;
  birth_date: string | null;
  sex: "female" | "male" | "other" | null;
  age_months: number | null;
  owner: UserBrief;
  care_team: Doctor[];
  created_at: string;
}

export interface SubjectWithSummary extends Subject {
  summary: Summary;
}

export interface DailyLog {
  id: number;
  log_date: string;
  mood: Mood;
  sleep_hours: number;
  social_interaction: number;
  meltdown: boolean;
  note: string | null;
  created_at: string;
}

export interface DailyLogInput {
  log_date: string;
  mood: Mood;
  sleep_hours: number;
  social_interaction: number;
  meltdown: boolean;
  note: string | null;
}

export interface Observation {
  id: number;
  author_id: number | null;
  sensory_sensitivity: number;
  eye_contact: number;
  communication: number;
  routine_adaptation: number;
  eating_pattern: string | null;
  therapy: string | null;
  self_harm_risk: "none" | "low" | "high";
  note: string | null;
  created_at: string;
}

export type ObservationInput = Omit<Observation, "id" | "author_id" | "created_at">;

export interface Contribution {
  item: number;
  short: string;
  answer: number;
  log_odds: number;
}

export interface Screening {
  id: number;
  instrument: Instrument;
  answers: Record<string, number>;
  score: number;
  risk_level: RiskLevel;
  details: {
    threshold?: number;
    model_version?: string;
    contributions?: Contribution[];
    scored_items?: number[];
  };
  created_at: string;
}

export interface InstrumentItem {
  item: number;
  question: string;
  options: string[];
  short?: string;
}

export interface Instruments {
  qchat10: {
    name: string;
    description: string;
    age_range_months: [number, number];
    items: InstrumentItem[];
    model: { version: string; label: string; threshold: number; sensitivity: number; specificity: number };
  };
  aq10: { name: string; description: string; items: InstrumentItem[]; threshold: number };
}

export interface Note {
  id: number;
  doctor: UserBrief | null;
  body: string;
  recommendation: string | null;
  next_visit: string | null;
  created_at: string;
}

export interface Alert {
  level: "info" | "warning" | "critical";
  code: string;
  message: string;
}

export interface Insights {
  stats: {
    n_logs: number;
    avg_sleep: number | null;
    avg_social: number | null;
    meltdown_days: number;
    mood_counts: Partial<Record<Mood, number>>;
    streak: number;
    logged_today: boolean;
  };
  series: { date: string; sleep_hours: number; social_interaction: number; mood: Mood; meltdown: boolean }[];
  alerts: Alert[];
  latest_screening: { id: number; instrument: Instrument; risk_level: RiskLevel; score: number; created_at: string } | null;
  next_visit: string | null;
}

export interface Message {
  id: number;
  sender_id: number;
  recipient_id: number;
  body: string;
  read_at: string | null;
  created_at: string;
}

export interface Conversation {
  user: UserBrief;
  last_message: Message | null;
  unread: number;
}

export interface Notification {
  id: number;
  kind: string;
  title: string;
  body: string;
  link: string | null;
  read_at: string | null;
  created_at: string;
}

export interface ModelReport {
  key: string;
  label: string;
  auc: { mean: number; std: number };
  brier: { mean: number; std: number };
  pooled_oof_auc: number;
  pooled_oof_auc_ci95: [number, number];
  folds_beating_baseline: number;
  roc_curve: { fpr: number[]; tpr: number[] };
}

export interface ModelCard {
  model_version: string;
  trained_on: string;
  chosen_model: string;
  chosen_model_label: string;
  selection_rule: string;
  hyperparameters: Record<string, unknown>;
  items: InstrumentItem[];
  threshold: number;
  operating_point: { threshold: number; sensitivity: number; specificity: number };
  calibration: { prob_pred: number[]; prob_true: number[] };
  baseline_total_score: { auc: { mean: number; std: number }; pooled_auc: number };
  models: ModelReport[];
  item_selection_frequency: { item: number; short: string; frequency: number }[];
  dataset: { name: string; n: number; n_asd: number; n_control: number; source: string; label_source: string };
  evaluation: { outer_cv: string; inner_cv: string; threshold_note: string };
}
