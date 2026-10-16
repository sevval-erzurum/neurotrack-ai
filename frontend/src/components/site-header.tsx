import { Logo } from "./brand";
import { ThemeToggle } from "./theme-toggle";
import { ButtonLink } from "./ui";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-page/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-8">
        <Logo />
        <nav className="flex items-center gap-1 sm:gap-2" aria-label="Site">
          <ButtonLink href="/model" variant="ghost" size="sm" className="hidden sm:inline-flex">
            Model kartı
          </ButtonLink>
          <ThemeToggle />
          <ButtonLink href="/login" variant="secondary" size="sm">
            Giriş
          </ButtonLink>
          <ButtonLink href="/register" size="sm" className="hidden sm:inline-flex">
            Ücretsiz başla
          </ButtonLink>
        </nav>
      </div>
    </header>
  );
}
