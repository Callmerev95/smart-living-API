import { Card } from "@/components/ui/Card";
import { content } from "@/lib/constants/content";

/**
 * Catatan keputusan teknis (`docs/content-schema.md` §B.10.5).
 *
 * Tiga kartu tampil seragam dengan alasan tertulis: trade-off punya bobot setara,
 * tidak ada yang perlu diutamakan (R-14). Setiap kartu menyebut trade-off, bukan
 * hanya keunggulan — bagian ini yang memperlihatkan reasoning.
 */
export function TechnicalDecisions() {
  return (
    <section className="flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-ink">{content.showcase.decisionsHeading}</h3>

      <div className="grid gap-3 md:grid-cols-3">
        {content.showcase.decisions.map((decision) => (
          <Card key={decision.title} className="flex flex-col gap-2 bg-surface p-4">
            <h4 className="text-sm font-semibold text-ink">{decision.title}</h4>
            <p className="text-xs leading-relaxed text-ink-soft">{decision.body}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}
