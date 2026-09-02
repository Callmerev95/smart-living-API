import { Badge } from "@/components/ui/Badge";
import { content } from "@/lib/constants/content";

export function HeroSection() {
  return (
    <section className="flex flex-col items-start gap-3">
      <Badge tone="info">{content.hero.badge}</Badge>
      <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 sm:text-4xl">
        {content.hero.title}
      </h1>
      <p className="max-w-2xl text-lg text-zinc-600">{content.hero.subtitle}</p>
    </section>
  );
}
