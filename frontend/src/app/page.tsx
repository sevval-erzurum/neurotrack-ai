import {
  ArrowRight,
  Baby,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  KeyRound,
  LineChart,
  LockKeyhole,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  UserRound,
} from "lucide-react";

import { LogoMark } from "@/components/brand";
import { SiteHeader } from "@/components/site-header";
import { ButtonLink, Card } from "@/components/ui";

const ROLES = [
  {
    icon: Baby,
    title: "Ebeveynler için",
    points: [
      "18–24 ay için klinik tanılarla eğitilmiş Q-CHAT-10 taraması",
      "Uyku, sosyal etkileşim, duygu durumu ve kriz takibi",
      "Doktorunuzu ekleyin, notlarını ve randevularını görün",
    ],
  },
  {
    icon: UserRound,
    title: "Yetişkinler için",
    points: ["AQ-10 öz-değerlendirme", "Günlük takip ve kişisel eğilimler", "Bakım ekibinizle güvenli mesajlaşma"],
  },
  {
    icon: Stethoscope,
    title: "Doktorlar için",
    points: [
      "Danışanlar uyarı ve risk düzeyine göre sıralı",
      "Ziyaretler arası veri: grafikler, gözlemler, tarama geçmişi",
      "Notlar ve sonraki görüşme tarihi tek yerde",
    ],
  },
];

const PRINCIPLES = [
  {
    icon: ClipboardCheck,
    title: "Dürüst değerlendirme",
    text: "Madde seçimi ve hiperparametre araması nested cross-validation içinde. Dört model karşılaştırıldı; fark gürültü düzeyinde olduğu için en açıklanabilir olan seçildi.",
  },
  {
    icon: BrainCircuit,
    title: "Her sonuç açıklanır",
    text: "Tarama sonucunda hangi yanıtın skoru ne kadar etkilediği gösterilir. Doğrusal modelde bu katkılar tam ve toplanabilirdir.",
  },
  {
    icon: LineChart,
    title: "Sızıntılı veriye hayır",
    text: "Etiketi soru toplamından türetilmiş popüler veri setleri ML için kullanılmaz. Orada yayımlanmış puanlama kuralı uygulanır.",
  },
];

const SECURITY = [
  { icon: KeyRound, text: "Erişimi verinin sahibi verir; doktorlar kendilerini ekleyemez." },
  { icon: LockKeyhole, text: "httpOnly oturum çerezi, hız sınırlama, ID tahminine karşı 404." },
  { icon: Sparkles, text: "Dil modeline isim veya kimlik bilgisi gönderilmez." },
  { icon: ShieldCheck, text: "Kriz ifadelerinde her durumda acil yardım bilgisi." },
];

export default function LandingPage() {
  return (
    <>
      <SiteHeader />
      <main>
        <section className="mx-auto grid max-w-6xl items-center gap-12 px-4 pt-14 pb-20 sm:px-8 lg:grid-cols-[1.1fr_1fr] lg:pt-20">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1 text-xs font-medium text-ink-2">
              <span className="size-1.5 rounded-full bg-brand" aria-hidden />
              Açıklanabilir yapay zekâ ile erken tarama
            </p>
            <h1 className="mt-5 text-4xl leading-[1.08] font-semibold tracking-tight text-balance sm:text-5xl">
              Erken fark edin, doğru uzmana zamanında ulaşın.
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-2">
              NeuroTrack; ebeveynlerin, otizmli yetişkinlerin ve hekimlerin aynı veriye bakarak birlikte karar vermesini
              sağlar. Tarama, günlük takip ve bakım ekibi iletişimi tek yerde.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <ButtonLink href="/login" size="lg">
                Demo hesapla dene
                <ArrowRight className="size-4" aria-hidden />
              </ButtonLink>
              <ButtonLink href="/model" size="lg" variant="secondary">
                Model kartını incele
              </ButtonLink>
            </div>
            <p className="mt-4 text-sm text-muted">Kayıt gerekmez: ebeveyn, yetişkin ve doktor demo hesapları hazır.</p>
          </div>

          <ProductPreview />
        </section>

        <section className="border-y border-line bg-surface">
          <div className="mx-auto grid max-w-6xl gap-8 px-4 py-16 sm:px-8 md:grid-cols-3">
            {ROLES.map(({ icon: Icon, title, points }) => (
              <div key={title}>
                <span className="grid size-10 place-items-center rounded-xl bg-brand-soft text-brand">
                  <Icon className="size-5" aria-hidden />
                </span>
                <h2 className="mt-4 font-semibold tracking-tight">{title}</h2>
                <ul className="mt-3 space-y-2">
                  {points.map((p) => (
                    <li key={p} className="flex gap-2 text-sm text-ink-2">
                      <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
                      {p}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-20 sm:px-8">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-brand">Yapay zekâ yaklaşımı</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight">Daha büyük model değil, daha dürüst model.</h2>
            <p className="mt-3 text-ink-2">
              252 çocukluk, klinik tanılı bir veri setinde karmaşık modeller ek kazanç sağlamıyor. Bunu kanıtlamak ve sonucu
              açıklayabilmek, bir sağlık uygulamasında daha yüksek bir skordan daha değerli.
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {PRINCIPLES.map(({ icon: Icon, title, text }) => (
              <Card key={title} className="p-6">
                <Icon className="size-5 text-brand" aria-hidden />
                <h3 className="mt-4 font-semibold tracking-tight">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-2">{text}</p>
              </Card>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-20 sm:px-8">
          <Card className="grid gap-8 p-8 md:grid-cols-[1fr_1.4fr] md:p-10">
            <div>
              <p className="text-sm font-medium text-brand">Gizlilik ve güvenlik</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">Sağlık verisi, sağlık verisi gibi korunur.</h2>
            </div>
            <ul className="grid gap-4 sm:grid-cols-2">
              {SECURITY.map(({ icon: Icon, text }) => (
                <li key={text} className="flex gap-3 text-sm text-ink-2">
                  <Icon className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden />
                  {text}
                </li>
              ))}
            </ul>
          </Card>
        </section>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <div className="flex items-center gap-2.5">
            <LogoMark className="size-6" />
            <span>NeuroTrack AI · Next.js, FastAPI, scikit-learn</span>
          </div>
          <p>Tanı aracı değildir. Endişeleriniz için bir uzmana başvurun.</p>
        </div>
      </footer>
    </>
  );
}

/** Ürün ekranından sadeleştirilmiş, statik bir önizleme. */
function ProductPreview() {
  const bars = [
    { label: "Göz teması", value: 0.62 },
    { label: "İlgi paylaşmak için işaret etme", value: 0.48 },
    { label: "Teselli etme", value: 0.41 },
    { label: "Nesneleri sıralama", value: -0.28 },
    { label: "Jest kullanımı", value: 0.22 },
  ];
  return (
    <div className="relative" aria-hidden>
      <div className="absolute -inset-6 -z-10 rounded-[32px] bg-gradient-to-br from-brand-soft via-transparent to-transparent" />
      <Card className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted">Q-CHAT-10 sonucu · Deniz, 21 aylık</p>
            <p className="mt-1 font-semibold">Uzman değerlendirmesi öneriliyor</p>
          </div>
          <span className="rounded-full bg-warning-soft px-2.5 py-1 text-xs font-medium text-warning-ink">Değerlendirme</span>
        </div>
        <div className="mt-5 space-y-2.5">
          {bars.map((b) => (
            <div key={b.label} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)] items-center gap-3">
              <span className="truncate text-xs text-ink-2">{b.label}</span>
              <div className="relative h-4">
                <div className="absolute inset-y-0 left-1/2 w-px bg-[var(--axis)]" />
                <div
                  className="absolute inset-y-0.5 rounded-[3px]"
                  style={{
                    background: b.value > 0 ? "var(--pole-pos)" : "var(--pole-neg)",
                    left: b.value > 0 ? "50%" : `${50 - Math.abs(b.value) * 70}%`,
                    width: `${Math.abs(b.value) * 70}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
      <Card className="mt-4 ml-10 p-5">
        <p className="text-xs text-muted">Uyku süresi · son 30 gün</p>
        <svg viewBox="0 0 300 70" className="mt-3 h-16 w-full">
          <line x1="0" x2="300" y1="44" y2="44" stroke="var(--grid)" />
          <polyline
            fill="none"
            stroke="var(--series-1)"
            strokeWidth="2"
            strokeLinejoin="round"
            strokeLinecap="round"
            points="0,52 20,48 40,50 60,44 80,46 100,40 120,42 140,36 160,38 180,32 200,30 220,33 240,26 260,24 280,27 300,22"
          />
        </svg>
      </Card>
    </div>
  );
}
