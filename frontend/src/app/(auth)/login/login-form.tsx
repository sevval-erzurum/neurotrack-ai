"use client";

import { useMutation } from "@tanstack/react-query";
import { ArrowRight, Baby, Stethoscope, UserRound } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button, Field, Input } from "@/components/ui";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";

const DEMO = [
  { email: "ebeveyn@example.com", label: "Ebeveyn", who: "Elif Demir · 2 çocuk", icon: Baby },
  { email: "yetiskin@example.com", label: "Yetişkin", who: "Mert Aksoy · kendi takibi", icon: UserRound },
  { email: "doktor@example.com", label: "Doktor", who: "Dr. Zeynep Kaya · 2 danışan", icon: Stethoscope },
];

function safeNext(value: string | null): string {
  // Açık yönlendirmeyi önle: yalnızca site içi yollar.
  return value && value.startsWith("/") && !value.startsWith("//") ? value : "/dashboard";
}

export function LoginForm() {
  const params = useSearchParams();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = useMutation({
    mutationFn: (body: { email: string; password: string }) => api<User>("/auth/login", { method: "POST", json: body }),
    onSuccess: () => router.replace(safeNext(params.get("next"))),
    meta: { silent: true },
  });

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Tekrar hoş geldiniz</h1>
      <p className="mt-1.5 text-sm text-ink-2">Hesabınıza giriş yapın.</p>

      <form
        className="mt-8 space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          login.mutate({ email, password });
        }}
      >
        <Field label="E-posta">
          {(id) => (
            <Input
              id={id}
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ornek@eposta.com"
            />
          )}
        </Field>
        <Field label="Şifre" error={login.error?.message}>
          {(id) => (
            <Input
              id={id}
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          )}
        </Field>
        <Button type="submit" className="w-full" loading={login.isPending}>
          Giriş yap
        </Button>
      </form>

      <p className="mt-5 text-center text-sm text-ink-2">
        Hesabınız yok mu?{" "}
        <Link href="/register" className="font-medium text-brand hover:underline">
          Kayıt olun
        </Link>
      </p>

      <div className="mt-10">
        <div className="flex items-center gap-3 text-xs font-medium uppercase tracking-wider text-muted">
          <span className="h-px flex-1 bg-line" />
          Demo hesaplarla keşfedin
          <span className="h-px flex-1 bg-line" />
        </div>
        <ul className="mt-4 space-y-2">
          {DEMO.map(({ email: demoEmail, label, who, icon: Icon }) => (
            <li key={demoEmail}>
              <button
                type="button"
                disabled={login.isPending}
                onClick={() => login.mutate({ email: demoEmail, password: "demo1234" })}
                className="group flex w-full items-center gap-3 rounded-xl border border-line bg-surface px-3.5 py-3 text-left transition-colors hover:border-line-strong hover:bg-surface-2 disabled:opacity-60"
              >
                <span className="grid size-9 place-items-center rounded-lg bg-brand-soft text-brand">
                  <Icon className="size-4" aria-hidden />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-medium">{label}</span>
                  <span className="block truncate text-xs text-muted">{who}</span>
                </span>
                <ArrowRight className="size-4 text-muted transition-transform group-hover:translate-x-0.5" aria-hidden />
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
