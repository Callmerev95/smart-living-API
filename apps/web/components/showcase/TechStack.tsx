import { content } from "@/lib/constants/content";

/**
 * Full width: layout 2 kolom `10rem 1fr` semula membuat nilai yang panjang
 * ("PostgreSQL-ready", "Actions") wrap 2 baris di kolom sempit. Satu baris per
 * layer lebih terbaca dan tetap ringkas.
 *
 * Layer (dt) memakai mono agar konsisten dengan data voice di seluruh halaman.
 */
export function TechStack() {
  return (
    <section className="flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-ink">{content.showcase.stackHeading}</h3>

      <dl className="flex flex-col divide-y divide-line rounded-xl border border-line bg-surface px-4 py-1">
        {content.showcase.stack.map((row) => (
          <div
            key={row.layer}
            className="flex flex-col gap-0.5 py-2.5 sm:flex-row sm:items-baseline sm:gap-3"
          >
            <dt className="w-24 shrink-0 font-mono text-xs font-semibold text-turmeric">
              {row.layer}
            </dt>
            <dd className="text-xs text-ink-soft sm:text-sm">{row.items}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
