"use client";

import { useMutation } from "@tanstack/react-query";
import { Info, Send, ShieldCheck, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Avatar, Badge, Button, Card, PageHeader, Select, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { cn } from "@/lib/cn";
import { useMe, useSubjects } from "@/lib/queries";

type Turn = { role: "user" | "assistant"; content: string; source?: "gemini" | "fallback" };

const SUGGESTIONS: Record<string, string[]> = {
  parent: [
    "Son iki haftanın kayıtlarını özetler misin?",
    "Kriz anında evde neler yapabilirim?",
    "Uyku rutinini nasıl oturtabiliriz?",
  ],
  adult: ["Bu haftaki kayıtlarımda dikkat çeken ne var?", "Kalabalık ortamlarda duyusal yüklenmeyle nasıl başa çıkarım?"],
  doctor: ["Bu danışanın son 14 günlük verisini klinik açıdan özetle.", "Q-CHAT-10'un 18–24 ay için sınırlılıkları nelerdir?"],
};

export default function AssistantPage() {
  const me = useMe();
  const subjects = useSubjects();
  // null: kullanıcı seçim yapmadı, ilk kişi varsayılır. "": bilerek bağlamsız.
  const [choice, setChoice] = useState<string | null>(null);
  const subjectId = choice ?? (subjects.data?.[0] ? String(subjects.data[0].id) : "");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [draft, setDraft] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => endRef.current?.scrollIntoView({ block: "end", behavior: "smooth" }), [turns.length]);

  const chat = useMutation({
    mutationFn: (message: string) =>
      api<{ reply: string; source: "gemini" | "fallback" }>("/assistant/chat", {
        method: "POST",
        json: {
          message,
          subject_id: subjectId ? Number(subjectId) : null,
          history: turns.slice(-10).map(({ role, content }) => ({ role, content })),
        },
      }),
    onSuccess: (data) => setTurns((t) => [...t, { role: "assistant", content: data.reply, source: data.source }]),
  });

  const ask = (text: string) => {
    const message = text.trim();
    if (!message || chat.isPending) return;
    setTurns((t) => [...t, { role: "user", content: message }]);
    setDraft("");
    chat.mutate(message);
  };

  const role = me.data?.role ?? "parent";

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title={
          <span className="flex items-center gap-2.5">
            <Sparkles className="size-6 text-brand" aria-hidden />
            Deva asistan
          </span>
        }
        description="Takip verilerine dayalı, destekleyici öneriler. Tanı koymaz, ilaç önermez."
        action={
          subjects.data && subjects.data.length > 0 && (
            <div className="flex items-center gap-2">
              <label htmlFor="ctx" className="text-sm text-muted">
                Bağlam
              </label>
              <Select id="ctx" value={subjectId} onChange={(e) => setChoice(e.target.value)} className="w-48">
                <option value="">Bağlam yok</option>
                {subjects.data.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.kind === "self" && s.owner.id === me.data?.id ? "Benim takibim" : s.name}
                  </option>
                ))}
              </Select>
            </div>
          )
        }
      />

      <Card className="flex h-[calc(100dvh-15rem)] min-h-[460px] flex-col">
        <div className="flex-1 space-y-5 overflow-y-auto p-5" aria-live="polite">
          {turns.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <span className="grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand">
                <Sparkles className="size-6" aria-hidden />
              </span>
              <p className="mt-3 font-medium">Size nasıl yardımcı olabilirim?</p>
              <div className="mt-5 flex max-w-xl flex-wrap justify-center gap-2">
                {(SUGGESTIONS[role] ?? SUGGESTIONS.parent).map((s) => (
                  <button
                    key={s}
                    onClick={() => ask(s)}
                    className="rounded-full border border-line-strong px-3.5 py-1.5 text-sm text-ink-2 transition-colors hover:bg-surface-2 hover:text-ink"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {turns.map((t, i) => (
            <div key={i} className={cn("flex gap-3", t.role === "user" && "flex-row-reverse")}>
              {t.role === "user" ? (
                <Avatar name={me.data?.full_name ?? "Sen"} className="size-8 text-[11px]" />
              ) : (
                <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand text-brand-ink">
                  <Sparkles className="size-4" aria-hidden />
                </span>
              )}
              <div className={cn("max-w-[82%]", t.role === "user" && "text-right")}>
                <div
                  className={cn(
                    "inline-block rounded-2xl px-4 py-2.5 text-left text-[15px] leading-relaxed whitespace-pre-line",
                    t.role === "user" ? "rounded-tr-md bg-primary text-primary-ink" : "rounded-tl-md bg-surface-2",
                  )}
                >
                  {t.content}
                </div>
                {t.source === "fallback" && (
                  <Badge className="mt-1.5" title="Dil modeli şu an kullanılamıyor; kural tabanlı yanıt verildi.">
                    <Info className="size-3" aria-hidden />
                    Kural tabanlı yanıt
                  </Badge>
                )}
              </div>
            </div>
          ))}
          {chat.isPending && (
            <div className="flex gap-3">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand text-brand-ink">
                <Sparkles className="size-4" aria-hidden />
              </span>
              <div className="flex items-center gap-1 rounded-2xl rounded-tl-md bg-surface-2 px-4 py-3" aria-label="Yanıt yazılıyor">
                {[0, 1, 2].map((d) => (
                  <span key={d} className="size-1.5 animate-bounce rounded-full bg-muted" style={{ animationDelay: `${d * 120}ms` }} />
                ))}
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form
          className="border-t border-line p-3"
          onSubmit={(e) => {
            e.preventDefault();
            ask(draft);
          }}
        >
          <div className="flex items-end gap-2">
            <label htmlFor="prompt" className="sr-only">
              Mesajınız
            </label>
            <Textarea
              id="prompt"
              rows={1}
              maxLength={2000}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  ask(draft);
                }
              }}
              placeholder="Bir soru sorun…"
              className="max-h-32 min-h-10 resize-none py-2"
            />
            <Button type="submit" size="icon" className="size-10 shrink-0" disabled={!draft.trim() || chat.isPending} aria-label="Gönder">
              <Send className="size-4" />
            </Button>
          </div>
          <p className="mt-2 flex items-center gap-1.5 text-[11px] text-muted">
            <ShieldCheck className="size-3.5" aria-hidden />
            Dil modeline isim veya kimlik bilgisi gönderilmez; yalnızca seçilen kişinin son 14 günlük özet istatistikleri.
          </p>
        </form>
      </Card>
    </div>
  );
}
