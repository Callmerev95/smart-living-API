import { content } from "@/lib/constants/content";

/**
 * Diagram alur request (`docs/content-schema.md` §B.10.3).
 *
 * Dibangun dari elemen DOM, bukan ASCII di dalam `<pre>`, agar tetap terbaca di
 * layar kecil. Nomor langkah memakai mono (data voice); deskripsi alur
 * disediakan lewat `aria-label` untuk screen reader.
 */
export function ArchitectureDiagram() {
  const steps = content.showcase.diagramFlow;

  return (
    <section className="flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-ink">{content.showcase.architectureHeading}</h3>

      <ol
        aria-label={content.showcase.diagramAlt}
        className="flex flex-col gap-2 rounded-xl border border-line bg-surface p-4"
      >
        {steps.map((step, index) => (
          <li key={step.label} className="flex flex-col gap-2">
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <span className="font-mono text-xs font-semibold text-turmeric tabular-nums">
                {String(index + 1).padStart(2, "0")}
              </span>
              <span className="rounded-md bg-surface-muted px-2 py-0.5 text-xs font-medium text-ink">
                {step.label}
              </span>
              <span className="text-xs text-ink-soft">{step.note}</span>
            </div>
            {index < steps.length - 1 && (
              <span aria-hidden="true" className="pl-3 text-xs leading-none text-ink-soft">
                ↓
              </span>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
