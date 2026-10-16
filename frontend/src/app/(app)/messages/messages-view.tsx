"use client";

import { ArrowLeft, MessageSquare, Send } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Avatar, Button, Card, EmptyState, ErrorState, PageHeader, Spinner, Textarea } from "@/components/ui";
import { cn } from "@/lib/cn";
import { ROLE_LABEL, formatDay, formatRelative, formatTime } from "@/lib/format";
import { keys, useConversations, useMe, useSendMessage, useThread } from "@/lib/queries";
import type { Conversation } from "@/lib/types";
import { useQueryClient } from "@tanstack/react-query";

export function MessagesView() {
  const params = useSearchParams();
  const router = useRouter();
  const peer = params.get("with") ? Number(params.get("with")) : null;
  const conversations = useConversations();
  const me = useMe();

  if (conversations.isPending || me.isPending) return <Spinner />;
  if (conversations.error) return <ErrorState error={conversations.error} retry={() => conversations.refetch()} />;

  const list = conversations.data;
  const active = list.find((c) => c.user.id === peer) ?? null;
  const open = (id: number | null) => router.replace(id ? `/messages?with=${id}` : "/messages", { scroll: false });

  return (
    <>
      <PageHeader
        title="Mesajlar"
        description={
          me.data?.role === "doctor"
            ? "Sizi bakım ekibine ekleyen danışanlar ve aileleriyle yazışmalar."
            : "Bakım ekibinizdeki doktorlarla güvenli yazışma."
        }
      />
      {list.length === 0 ? (
        <Card>
          <EmptyState
            icon={<MessageSquare className="size-5" />}
            title="Henüz yazışabileceğiniz kimse yok"
            description="Mesajlaşma, bakım ekibi ilişkisi olan doktor ve aile arasında açılır."
          />
        </Card>
      ) : (
        <Card className="grid h-[calc(100dvh-14rem)] min-h-[480px] overflow-hidden md:grid-cols-[300px_1fr]">
          <ul className={cn("divide-y divide-line overflow-y-auto border-line md:border-r", active && "hidden md:block")}>
            {list.map((c) => (
              <ConversationRow key={c.user.id} conversation={c} active={c.user.id === peer} onClick={() => open(c.user.id)} />
            ))}
          </ul>
          {active ? (
            <Thread key={active.user.id} conversation={active} myId={me.data!.id} onBack={() => open(null)} />
          ) : (
            <div className="hidden items-center justify-center md:flex">
              <p className="text-sm text-muted">Bir konuşma seçin.</p>
            </div>
          )}
        </Card>
      )}
    </>
  );
}

function ConversationRow({ conversation: c, active, onClick }: { conversation: Conversation; active: boolean; onClick: () => void }) {
  return (
    <li>
      <button
        onClick={onClick}
        aria-current={active ? "true" : undefined}
        className={cn("flex w-full gap-3 px-4 py-3.5 text-left transition-colors", active ? "bg-surface-2" : "hover:bg-surface-2/60")}
      >
        <Avatar name={c.user.full_name} />
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-2">
            <p className={cn("truncate text-sm", c.unread ? "font-semibold" : "font-medium")}>{c.user.full_name}</p>
            {c.last_message && <span className="shrink-0 text-[11px] text-muted">{formatRelative(c.last_message.created_at)}</span>}
          </div>
          <div className="flex items-center gap-2">
            <p className={cn("flex-1 truncate text-sm", c.unread ? "text-ink" : "text-muted")}>
              {c.last_message?.body ?? ROLE_LABEL[c.user.role]}
            </p>
            {c.unread > 0 && (
              <span className="tabular grid min-w-5 place-items-center rounded-full bg-brand px-1.5 text-[11px] font-semibold leading-5 text-brand-ink">
                {c.unread}
              </span>
            )}
          </div>
        </div>
      </button>
    </li>
  );
}

function Thread({ conversation, myId, onBack }: { conversation: Conversation; myId: number; onBack: () => void }) {
  const thread = useThread(conversation.user.id);
  const send = useSendMessage(conversation.user.id);
  const qc = useQueryClient();
  const [draft, setDraft] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const count = thread.data?.length ?? 0;

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [count]);

  // Konuşma açıldığında API mesajları okundu işaretler; listedeki sayaç güncellensin.
  useEffect(() => {
    if (thread.isSuccess) qc.invalidateQueries({ queryKey: keys.conversations });
  }, [thread.isSuccess, qc]);

  const submit = () => {
    const body = draft.trim();
    if (!body) return;
    send.mutate(body, { onSuccess: () => setDraft("") });
  };

  let lastDay = "";

  return (
    <section className="flex min-h-0 flex-col" aria-label={`${conversation.user.full_name} ile konuşma`}>
      <header className="flex items-center gap-3 border-b border-line px-4 py-3">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={onBack} aria-label="Konuşmalara dön">
          <ArrowLeft className="size-4" />
        </Button>
        <Avatar name={conversation.user.full_name} />
        <div>
          <p className="text-sm font-semibold">{conversation.user.full_name}</p>
          <p className="text-xs text-muted">{ROLE_LABEL[conversation.user.role]}</p>
        </div>
      </header>

      <div className="flex-1 space-y-1.5 overflow-y-auto bg-page/40 px-4 py-4" aria-live="polite">
        {thread.isPending && <Spinner />}
        {thread.data?.length === 0 && <p className="py-10 text-center text-sm text-muted">İlk mesajı siz yazın.</p>}
        {thread.data?.map((m) => {
          const mine = m.sender_id === myId;
          const day = m.created_at.slice(0, 10);
          const showDay = day !== lastDay;
          lastDay = day;
          return (
            <div key={m.id}>
              {showDay && (
                <p className="py-3 text-center text-[11px] font-medium text-muted">{formatDay(day)}</p>
              )}
              <div className={cn("flex", mine ? "justify-end" : "justify-start")}>
                <div
                  className={cn(
                    "max-w-[78%] rounded-2xl px-3.5 py-2 text-[15px] leading-snug",
                    mine ? "rounded-br-md bg-primary text-primary-ink" : "rounded-bl-md border border-line bg-surface",
                  )}
                >
                  <p className="whitespace-pre-line">{m.body}</p>
                  <p className={cn("mt-0.5 text-right text-[10px]", mine ? "opacity-60" : "text-muted")}>
                    {formatTime(m.created_at)}
                    {mine && m.read_at && " · okundu"}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>

      <form
        className="flex items-end gap-2 border-t border-line p-3"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <label htmlFor="message" className="sr-only">
          Mesaj
        </label>
        <Textarea
          id="message"
          rows={1}
          value={draft}
          maxLength={4000}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Mesaj yazın…  (Enter gönderir, Shift+Enter yeni satır)"
          className="max-h-32 min-h-10 resize-none py-2"
        />
        <Button type="submit" size="icon" className="size-10 shrink-0" loading={send.isPending} aria-label="Gönder" disabled={!draft.trim()}>
          {!send.isPending && <Send className="size-4" />}
        </Button>
      </form>
    </section>
  );
}
