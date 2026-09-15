import { content } from "@/lib/constants/content";

/**
 * Layer (dt) memakai mono agar konsisten dengan data voice di seluruh halaman.
 */
export function TechStack() {
  return (
    <section className="flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-ink">{content.showcase.stackHeading}</h3>

      <dl className="grid gap-x-4 gap-y-2 rounded-xl border border-line bg-surface p-4 sm:grid-cols-[10rem_1fr]">
        {content.showcase.stack.map((row) => (
          <div key={row.layer} className="contents">
            <dt className="font-mono text-xs font-semibold text-turmeric">{row.layer}</dt>
            <dd className="text-xs text-ink-soft sm:text-sm">{row.items}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
