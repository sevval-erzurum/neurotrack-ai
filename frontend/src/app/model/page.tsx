import { AlertTriangle } from "lucide-react";
import type { Metadata } from "next";

import { SiteHeader } from "@/components/site-header";
import { Card, EmptyState } from "@/components/ui";
import type { ModelCard } from "@/lib/types";

import { ModelCardView } from "./model-card-view";

export const metadata: Metadata = {
  title: "Model kartı",
  description: "Q-CHAT kısa form tarama modelinin nested cross-validation sonuçları, kalibrasyonu ve sınırlılıkları.",
};

// Derleme sırasında API'ye ulaşılamayabilir (ör. Docker build); sayfa istek anında üretilir.
export const dynamic = "force-dynamic";

async function getModelCard(): Promise<ModelCard | null> {
  const base = process.env.API_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${base}/api/v1/model/card`, { next: { revalidate: 3600 } });
    return response.ok ? ((await response.json()) as ModelCard) : null;
  } catch {
    return null;
  }
}

export default async function ModelPage() {
  const card = await getModelCard();
  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-8">
        {card ? (
          <ModelCardView card={card} />
        ) : (
          <Card>
            <EmptyState
              icon={<AlertTriangle className="size-5" />}
              title="Model kartı şu an yüklenemiyor"
              description="API sunucusuna ulaşılamadı. Biraz sonra tekrar deneyin."
            />
          </Card>
        )}
      </main>
    </>
  );
}
