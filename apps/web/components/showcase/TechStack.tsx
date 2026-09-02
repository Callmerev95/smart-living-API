import { content } from "@/lib/constants/content";

export function TechStack() {
  return (
    <section className="flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-zinc-900">{content.showcase.stackHeading}</h3>

      <dl className="grid gap-2 rounded-lg border border-zinc-200 bg-white p-4 sm:grid-cols-[10rem_1fr]">
        {content.showcase.stack.map((row) => (
          <div key={row.layer} className="contents">
            <dt className="text-xs font-medium text-zinc-900">{row.layer}</dt>
            <dd className="text-xs text-zinc-600">{row.items}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
