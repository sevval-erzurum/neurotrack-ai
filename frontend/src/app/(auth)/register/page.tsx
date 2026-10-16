"use client";

import { useMutation } from "@tanstack/react-query";
import { Baby, Stethoscope, UserRound } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button, Field, Input } from "@/components/ui";
import { api } from "@/lib/api";
import { cn } from "@/lib/cn";
import { todayISO } from "@/lib/format";
import type { Role, User } from "@/lib/types";

const ROLES: { value: Role; title: string; text: string; icon: typeof Baby }[] = [
  { value: "parent", title: "Ebeveyn", text: "Çocuğumun gelişimini takip edeceğim", icon: Baby },
  { value: "adult", title: "Yetişkin", text: "Kendi takibimi yapacağım", icon: UserRound },
  { value: "doctor", title: "Doktor", text: "Danışanlarımı izleyeceğim", icon: Stethoscope },
];

export default function RegisterPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>("parent");
  const [form, setForm] = useState({ full_name: "", email: "", password: "", birth_date: "" });

  const register = useMutation({
    mutationFn: () =>
      api<User>("/auth/register", {
        method: "POST",
        json: { ...form, role, birth_date: role === "adult" && form.birth_date ? form.birth_date : null },
      }),
    onSuccess: () => router.replace("/dashboard"),
    meta: { silent: true },
  });

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Hesap oluşturun</h1>
      <p className="mt-1.5 text-sm text-ink-2">Rolünüze göre çalışma alanınız hazırlanır.</p>

      <form
        className="mt-8 space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          register.mutate();
        }}
      >
        <fieldset>
          <legend className="mb-1.5 text-sm font-medium">Rol</legend>
          <div className="grid grid-cols-3 gap-2">
            {ROLES.map(({ value, title, text, icon: Icon }) => (
              <label
                key={value}
                className={cn(
                  "cursor-pointer rounded-xl border px-2.5 py-3 text-center transition-colors has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-focus",
                  role === value ? "border-brand bg-brand-soft" : "border-line-strong hover:bg-surface-2",
                )}
              >
                <input
                  type="radio"
                  name="role"
                  value={value}
                  checked={role === value}
                  onChange={() => setRole(value)}
                  className="sr-only"
                />
                <Icon className={cn("mx-auto size-5", role === value ? "text-brand" : "text-ink-2")} aria-hidden />
                <span className="mt-1.5 block text-sm font-medium">{title}</span>
                <span className="mt-0.5 block text-[11px] leading-tight text-muted">{text}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <Field label="Ad soyad">
          {(id) => <Input id={id} required minLength={2} autoComplete="name" value={form.full_name} onChange={set("full_name")} />}
        </Field>
        <Field label="E-posta">
          {(id) => <Input id={id} type="email" required autoComplete="email" value={form.email} onChange={set("email")} />}
        </Field>
        <Field label="Şifre" hint="En az 8 karakter.">
          {(id) => (
            <Input
              id={id}
              type="password"
              required
              minLength={8}
              maxLength={72}
              autoComplete="new-password"
              value={form.password}
              onChange={set("password")}
            />
          )}
        </Field>
        {role === "adult" && (
          <Field label="Doğum tarihi" hint="AQ-10 taraması 16 yaş ve üzeri için geçerlidir.">
            {(id) => <Input id={id} type="date" max={todayISO()} value={form.birth_date} onChange={set("birth_date")} />}
          </Field>
        )}

        {register.error && (
          <p className="rounded-xl bg-critical-soft px-3 py-2.5 text-sm text-critical-ink" role="alert">
            {register.error.message}
          </p>
        )}
        <Button type="submit" className="w-full" loading={register.isPending}>
          Hesabı oluştur
        </Button>
      </form>

      <p className="mt-5 text-center text-sm text-ink-2">
        Zaten hesabınız var mı?{" "}
        <Link href="/login" className="font-medium text-brand hover:underline">
          Giriş yapın
        </Link>
      </p>
    </div>
  );
}
