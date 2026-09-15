"use client";

import { content } from "@/lib/constants/content";

/**
 * Toggle tema class-based (`.dark` di <html>), disetel lebih awal oleh script
 * di `app/layout.tsx`. Tanpa state React: ikon diganti lewat varian dark, jadi
 * tidak ada risiko hydration mismatch.
 */
export function ThemeToggle() {
  function toggleTheme() {
    const el = document.documentElement;
    const next = !el.classList.contains("dark");
    el.classList.toggle("dark", next);
    el.style.colorScheme = next ? "dark" : "light";
    try {
      // window.localStorage, bukan global bare: runner test (Node) punya global
      // localStorage eksperimental yang tidak berfungsi tanpa flag.
      window.localStorage.setItem("sl-theme", next ? "dark" : "light");
    } catch {
      // localStorage bisa diblokir (private mode). Tema tetap berlaku untuk
      // tab ini, hanya tidak tersimpan.
    }
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={content.theme.switchLabel}
      className="inline-flex size-11 items-center justify-center rounded-lg border border-line bg-surface text-ink transition-colors hover:bg-surface-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid focus-visible:outline-turmeric"
    >
      {/* Sun/moon: satu-satunya ikon yang relevan untuk kontrol tema (R-04). */}
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        className="hidden size-4 dark:block"
      >
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </svg>
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="size-4 dark:hidden"
      >
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
      </svg>
    </button>
  );
}
