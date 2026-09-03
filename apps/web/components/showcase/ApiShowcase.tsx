import { ArchitectureDiagram } from "@/components/showcase/ArchitectureDiagram";
import { RequestExample } from "@/components/showcase/RequestExample";
import { ResponseExample } from "@/components/showcase/ResponseExample";
import { TechStack } from "@/components/showcase/TechStack";
import { TechnicalDecisions } from "@/components/showcase/TechnicalDecisions";
import { getDocsUrl } from "@/lib/api/docs";
import { content } from "@/lib/constants/content";

/**
 * Area portfolio (`docs/content-schema.md` §B.10).
 *
 * Ditempatkan di bawah alur fungsional agar tidak mengganggu journey utama
 * (PRD §5: prioritaskan satu journey yang sangat baik). Eyebrow "Untuk developer"
 * menegaskan pemisahan itu secara visual.
 */
export function ApiShowcase() {
  return (
    <section className="flex flex-col gap-6 border-t border-zinc-200 pt-10">
      <div className="flex flex-col gap-1">
        <p className="text-xs font-semibold uppercase tracking-wide text-amber-700">
          {content.showcase.eyebrow}
        </p>
        <h2 className="text-2xl font-semibold text-zinc-900">{content.showcase.heading}</h2>
        <p className="text-sm text-zinc-600">{content.showcase.subheading}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <RequestExample />
        <ResponseExample />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ArchitectureDiagram />
        <TechStack />
      </div>

      <TechnicalDecisions />

      <a
        href={getDocsUrl()}
        className="w-fit text-sm font-medium text-zinc-700 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
      >
        {content.showcase.docsLabel}
      </a>
    </section>
  );
}
