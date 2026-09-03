import Link from "next/link";

import { getDocsUrl } from "@/lib/api/docs";
import { REPO_URL } from "@/lib/constants/links";
import { content } from "@/lib/constants/content";

/**
 * Header situs — hanya navigasi, tanpa logika bisnis
 * (`docs/component-architecture.md` §12). Copy dari `content.ts`.
 */
export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
        >
          <span aria-hidden="true" className="size-2.5 rounded-full bg-amber-500" />
          {content.brand.name}
        </Link>

        <nav aria-label={content.brand.navLabel} className="flex items-center gap-5">
          <a
            href={getDocsUrl()}
            className="text-sm font-medium text-zinc-600 transition-colors hover:text-zinc-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
          >
            {content.brand.nav.docs}
          </a>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-zinc-600 transition-colors hover:text-zinc-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
          >
            {content.brand.nav.repo}
          </a>
        </nav>
      </div>
    </header>
  );
}
