import { content } from "@/lib/constants/content";

/**
 * Hero tanpa badge kapsul: klaim "API-first, deterministic" tampil sebagai
 * baris mono kecil (data voice, DESIGN.md) di atas heading display serif.
 */
export function HeroSection() {
  return (
    <section className="flex flex-col gap-4">
      <p className="inline-flex items-center gap-2 font-mono text-xs font-medium text-turmeric">
        <span aria-hidden="true" className="size-1.5 rounded-full bg-clay" />
        {content.hero.badge}
      </p>
      <h1 className="max-w-2xl font-display text-4xl leading-tight font-semibold tracking-tight text-ink sm:text-5xl">
        {content.hero.title}
      </h1>
      <p className="max-w-xl text-lg text-ink-soft">{content.hero.subtitle}</p>
    </section>
  );
}
