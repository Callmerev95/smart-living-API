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
 * Susunan vertikal penuh lebar, bukan dua grid 2 kolom: isi tiap blok punya
 * tinggi yang jauh berbeda (request pendek, response panjang, arsitektur
 * panjang, stack pendek), jadi memaksanya bersebelahan meninggalkan ruang
 * kosong besar dan membuat response butuh scroll horizontal. Urutan mengikuti
 * narasi: kirim, terima, bagaimana bekerja, dengan apa, kenapa begini.
 *
 * Satu band surface-muted memisahkan area developer dari alur user utama
 * (PRD §5): hierarki lewat permukaan, bukan warna tambahan.
 */
export function ApiShowcase() {
  return (
    <section className="flex flex-col gap-8 rounded-xl border border-line bg-surface-muted p-6 sm:p-8">
      <div className="flex flex-col gap-1">
        <p className="font-mono text-xs font-medium text-turmeric">
          {content.showcase.eyebrow}
        </p>
        <h2 className="font-display text-2xl font-semibold text-ink">
          {content.showcase.heading}
        </h2>
        <p className="text-sm text-ink-soft">{content.showcase.subheading}</p>
      </div>

      {/* Pasangan request-response: gap 4 di dalam grup, 8 antar grup (2x). */}
      <div className="flex flex-col gap-4">
        <RequestExample />
        <ResponseExample />
      </div>

      <ArchitectureDiagram />

      <TechStack />

      <TechnicalDecisions />

      <a
        href={getDocsUrl()}
        className="w-fit text-sm font-medium text-ink underline underline-offset-4 hover:text-clay focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid focus-visible:outline-turmeric"
      >
        {content.showcase.docsLabel}
      </a>
    </section>
  );
}
