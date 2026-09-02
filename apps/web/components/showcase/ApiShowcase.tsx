import { ArchitectureDiagram } from "@/components/showcase/ArchitectureDiagram";
import { RequestExample } from "@/components/showcase/RequestExample";
import { ResponseExample } from "@/components/showcase/ResponseExample";
import { TechStack } from "@/components/showcase/TechStack";
import { TechnicalDecisions } from "@/components/showcase/TechnicalDecisions";
import { content } from "@/lib/constants/content";

/** URL dokumentasi OpenAPI, dibangun dari base URL API — tidak hardcode. */
function openApiDocsUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
  return `${base.replace(/\/$/, "")}/docs`;
}

/**
 * Area portfolio (`docs/content-schema.md` §B.10).
 *
 * Ditempatkan di bawah alur fungsional agar tidak mengganggu journey utama
 * (PRD §5: prioritaskan satu journey yang sangat baik).
 */
export function ApiShowcase() {
  return (
    <section className="flex flex-col gap-6 border-t border-zinc-200 pt-10">
      <div className="flex flex-col gap-1">
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
        href={openApiDocsUrl()}
        className="w-fit text-sm font-medium text-zinc-700 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
      >
        {content.showcase.docsLabel}
      </a>
    </section>
  );
}
