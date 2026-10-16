"use client";

import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { Toaster, toast } from "sonner";

import { ApiError } from "@/lib/api";

let redirecting = false;

function redirectToLogin() {
  if (redirecting || window.location.pathname.startsWith("/login")) return;
  redirecting = true;
  const next = encodeURIComponent(window.location.pathname + window.location.search);
  // Süresi dolmuş cookie temizlenmezse proxy /login'i tekrar /dashboard'a yönlendirir.
  fetch("/api/v1/auth/logout", { method: "POST" }).finally(() =>
    // Tam yeniden yükleme bilinçli: önbellekteki başka kullanıcının verisi temizlenir.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign(`/login?next=${next}`),
  );
}

export function Providers({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: (count, error) => !(error instanceof ApiError && error.status < 500) && count < 2,
            refetchOnWindowFocus: false,
          },
        },
        queryCache: new QueryCache({
          onError: (error) => {
            if (error instanceof ApiError && error.status === 401) redirectToLogin();
          },
        }),
        mutationCache: new MutationCache({
          onError: (error, _variables, _result, mutation) => {
            if (mutation.meta?.silent) return; // form hatayı kendi içinde gösteriyor
            if (error instanceof ApiError && error.status === 401) return redirectToLogin();
            toast.error(error.message);
          },
        }),
      }),
  );

  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster position="bottom-right" richColors closeButton />
    </QueryClientProvider>
  );
}
