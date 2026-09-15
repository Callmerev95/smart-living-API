import Link from "next/link";

import { getDocsUrl } from "@/lib/api/docs";
import { REPO_URL } from "@/lib/constants/links";
import { content } from "@/lib/constants/content";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

/**
 * Header situs — hanya navigasi, tanpa logika bisnis
 * (`docs/component-architecture.md` §12). Copy dari `content.ts`.
 *
 * Backdrop-blur hanya di sini (satu-satunya elemen kaca di halaman, R-10):
 * header menempel di atas konten yang menggulir.
 */
export function Header() {
  const focusRing =
    "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid focus-visible:outline-turmeric";

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-4 sm:px-6">
        <Link
          href="/"
          className={`inline-flex shrink-0 items-center gap-2 text-sm font-semibold whitespace-nowrap text-ink ${focusRing}`}
        >
          {/* Titik clay: motif identitas (DESIGN.md), satu per brand mark. */}
          <span aria-hidden="true" className="size-2.5 rounded-full bg-clay" />
          {content.brand.name}
        </Link>

        <div className="flex items-center gap-2 sm:gap-4">
          <nav
            aria-label={content.brand.navLabel}
            className="flex items-center gap-3 whitespace-nowrap sm:gap-5"
          >
            <a
              href={getDocsUrl()}
              className={`text-sm font-medium text-ink-soft transition-colors hover:text-ink ${focusRing}`}
            >
              {content.brand.nav.docs}
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className={`text-sm font-medium text-ink-soft transition-colors hover:text-ink ${focusRing}`}
            >
              {content.brand.nav.repo}
            </a>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
