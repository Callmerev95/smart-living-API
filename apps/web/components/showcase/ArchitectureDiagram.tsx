import { content } from "@/lib/constants/content";

/**
 * Diagram alur request (`docs/content-schema.md` §B.10.3).
 *
 * Dibangun dari elemen DOM, bukan ASCII di dalam `<pre>`, agar tetap terbaca di
 * layar kecil. Deskripsi alur disediakan lewat `aria-label` untuk screen reader.
 */
export function ArchitectureDiagram() {
  const steps = content.showcase.diagramFlow;

  return (
    <section className="flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-zinc-900">
        {content.showcase.architectureHeading}
      </h3>

      <ol
        aria-label={content.showcase.diagramAlt}
        className="flex flex-col gap-2 rounded-lg border border-zinc-200 bg-white p-4"
      >
        {steps.map((step, index) => (
          <li key={step.label} className="flex flex-col gap-2">
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <span className="rounded-md bg-zinc-100 px-2 py-1 text-xs font-medium text-zinc-900">
                {step.label}
              </span>
              <span className="text-xs text-zinc-500">{step.note}</span>
            </div>
            {index < steps.length - 1 && (
              <span aria-hidden="true" className="pl-3 text-xs leading-none text-zinc-400">
                ↓
              </span>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
