"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./api";
import type {
  Conversation,
  DailyLog,
  DailyLogInput,
  Doctor,
  Insights,
  Instrument,
  Instruments,
  Message,
  Note,
  Notification,
  Observation,
  ObservationInput,
  Screening,
  Subject,
  SubjectWithSummary,
  User,
} from "./types";

export const keys = {
  me: ["me"] as const,
  subjects: ["subjects"] as const,
  subject: (id: number) => ["subjects", id] as const,
  insights: (id: number, days: number) => ["subjects", id, "insights", days] as const,
  logs: (id: number) => ["subjects", id, "logs"] as const,
  observations: (id: number) => ["subjects", id, "observations"] as const,
  screenings: (id: number) => ["subjects", id, "screenings"] as const,
  notes: (id: number) => ["subjects", id, "notes"] as const,
  conversations: ["conversations"] as const,
  thread: (peer: number) => ["conversations", peer] as const,
  notifications: ["notifications"] as const,
  instruments: ["instruments"] as const,
};

// --- Oturum ----------------------------------------------------------------

export const useMe = () => useQuery({ queryKey: keys.me, queryFn: () => api<User>("/auth/me"), retry: false });

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<void>("/auth/logout", { method: "POST" }),
    onSettled: () => qc.clear(),
  });
}

// --- Takip edilen kişiler ---------------------------------------------------

export const useSubjects = () =>
  useQuery({ queryKey: keys.subjects, queryFn: () => api<SubjectWithSummary[]>("/subjects") });

export const useSubject = (id: number) =>
  useQuery({ queryKey: keys.subject(id), queryFn: () => api<Subject>(`/subjects/${id}`) });

export const useInsights = (id: number, days = 30) =>
  useQuery({ queryKey: keys.insights(id, days), queryFn: () => api<Insights>(`/subjects/${id}/insights?days=${days}`) });

export function useCreateChild() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; birth_date: string; sex: string | null }) =>
      api<Subject>("/subjects", { method: "POST", json: data }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.subjects }),
  });
}

export function useDeleteSubject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api<void>(`/subjects/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.subjects }),
  });
}

export function useAddDoctor(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (email: string) => api<Doctor>(`/subjects/${subjectId}/care-team`, { method: "POST", json: { email } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.subjects }),
  });
}

export function useRemoveDoctor(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (doctorId: number) => api<void>(`/subjects/${subjectId}/care-team/${doctorId}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.subjects }),
  });
}

// --- Kayıtlar ---------------------------------------------------------------

export const useLogs = (id: number) =>
  useQuery({ queryKey: keys.logs(id), queryFn: () => api<DailyLog[]>(`/subjects/${id}/logs?days=120`) });

export function useSaveLog(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DailyLogInput) => api<DailyLog>(`/subjects/${subjectId}/logs`, { method: "PUT", json: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.subject(subjectId) });
      qc.invalidateQueries({ queryKey: keys.subjects });
    },
  });
}

export function useDeleteLog(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (logId: number) => api<void>(`/subjects/${subjectId}/logs/${logId}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.subject(subjectId) }),
  });
}

export const useObservations = (id: number) =>
  useQuery({ queryKey: keys.observations(id), queryFn: () => api<Observation[]>(`/subjects/${id}/observations`) });

export function useAddObservation(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ObservationInput) =>
      api<Observation>(`/subjects/${subjectId}/observations`, { method: "POST", json: data }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.subject(subjectId) }),
  });
}

export const useNotes = (id: number) =>
  useQuery({ queryKey: keys.notes(id), queryFn: () => api<Note[]>(`/subjects/${id}/notes`) });

export function useAddNote(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { body: string; recommendation: string | null; next_visit: string | null }) =>
      api<Note>(`/subjects/${subjectId}/notes`, { method: "POST", json: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.subject(subjectId) });
      qc.invalidateQueries({ queryKey: keys.subjects });
    },
  });
}

// --- Taramalar --------------------------------------------------------------

export const useInstruments = () =>
  useQuery({ queryKey: keys.instruments, queryFn: () => api<Instruments>("/screenings/instruments"), staleTime: Infinity });

export const useScreenings = (id: number) =>
  useQuery({ queryKey: keys.screenings(id), queryFn: () => api<Screening[]>(`/subjects/${id}/screenings`) });

export const useScreening = (subjectId: number, screeningId: number) =>
  useQuery({
    queryKey: [...keys.screenings(subjectId), screeningId],
    queryFn: () => api<Screening>(`/subjects/${subjectId}/screenings/${screeningId}`),
  });

export function useRunScreening(subjectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { instrument: Instrument; answers: Record<number, number> }) =>
      api<Screening>(`/subjects/${subjectId}/screenings`, { method: "POST", json: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.subject(subjectId) });
      qc.invalidateQueries({ queryKey: keys.subjects });
    },
  });
}

// --- İletişim ---------------------------------------------------------------

export const useConversations = () =>
  useQuery({ queryKey: keys.conversations, queryFn: () => api<Conversation[]>("/conversations"), refetchInterval: 15_000 });

export const useThread = (peer: number | null) =>
  useQuery({
    queryKey: keys.thread(peer ?? 0),
    queryFn: () => api<Message[]>(`/conversations/${peer}/messages`),
    enabled: peer !== null,
    refetchInterval: 5_000,
  });

export function useSendMessage(peer: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: string) => api<Message>(`/conversations/${peer}/messages`, { method: "POST", json: { body } }),
    onSuccess: (message) => {
      qc.setQueryData<Message[]>(keys.thread(peer), (old) => [...(old ?? []), message]);
      qc.invalidateQueries({ queryKey: keys.conversations });
    },
  });
}

export const useNotifications = () =>
  useQuery({ queryKey: keys.notifications, queryFn: () => api<Notification[]>("/notifications"), refetchInterval: 30_000 });

export function useMarkNotification() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | "all") =>
      api<void>(id === "all" ? "/notifications/read-all" : `/notifications/${id}/read`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.notifications }),
  });
}
