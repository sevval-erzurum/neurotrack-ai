import type { Metadata } from "next";

import { SiteHeader } from "@/components/site-header";

import { ModelCardView } from "./model-card-view";

export const metadata: Metadata = {
  title: "Model kartı",
  description: "Q-CHAT-10 tarama modelinin nested cross-validation sonuçları, kalibrasyonu ve sınırlılıkları.",
};

export default function ModelPage() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-8">
        <ModelCardView />
      </main>
    </>
  );
}
