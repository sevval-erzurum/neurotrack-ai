import { BrainCircuit, LockKeyhole, Stethoscope } from "lucide-react";

import { Logo } from "@/components/brand";

const POINTS = [
  {
    icon: BrainCircuit,
    title: "Açıklanabilir erken tarama",
    text: "Gerçek tanılarla eğitilmiş model, sonucu hangi yanıtların etkilediğini gösterir.",
  },
  {
    icon: Stethoscope,
    title: "Bakım ekibiyle tek yerde",
    text: "Günlük kayıtlar, klinik gözlemler ve doktor notları aynı zaman çizelgesinde.",
  },
  {
    icon: LockKeyhole,
    title: "Erişimi siz verirsiniz",
    text: "Verinizi yalnızca sizin eklediğiniz doktorlar görebilir.",
  },
];

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-dvh lg:grid-cols-[1fr_minmax(0,560px)]">
      <main className="flex flex-col px-5 py-6 sm:px-10">
        <Logo />
        <div className="flex flex-1 items-center justify-center py-10">
          <div className="w-full max-w-sm">{children}</div>
        </div>
        <p className="text-xs text-muted">
          NeuroTrack tanı koymaz. Sonuçlar yalnızca uzman değerlendirmesine yönlendirme amaçlıdır.
        </p>
      </main>

      <aside className="relative hidden overflow-hidden bg-[#0c2723] p-12 text-[#e9f3f1] lg:flex lg:flex-col lg:justify-between">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 15%, #1c6b5e 0, transparent 45%), radial-gradient(circle at 85% 80%, #12443c 0, transparent 50%)",
          }}
          aria-hidden
        />
        <div className="relative">
          <p className="text-sm font-medium uppercase tracking-[0.14em] text-[#7fd1c1]">NeuroTrack AI</p>
          <h2 className="mt-4 max-w-md text-3xl font-semibold leading-tight tracking-tight">
            Erken fark etmek, doğru uzmana zamanında ulaşmak.
          </h2>
        </div>
        <ul className="relative space-y-6">
          {POINTS.map(({ icon: Icon, title, text }) => (
            <li key={title} className="flex gap-4">
              <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-white/10">
                <Icon className="size-5 text-[#7fd1c1]" aria-hidden />
              </span>
              <div>
                <p className="font-medium">{title}</p>
                <p className="mt-0.5 text-sm text-[#b5cfca]">{text}</p>
              </div>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
