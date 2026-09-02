import { CopyButton } from "@/components/ui/CopyButton";
import { API_EXAMPLE_RESPONSE_TEXT } from "@/lib/constants/apiExample";
import { content } from "@/lib/constants/content";

export function ResponseExample() {
  return (
    <section className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-zinc-900">
          {content.showcase.responseHeading}
        </h3>
        <CopyButton
          value={API_EXAMPLE_RESPONSE_TEXT}
          label={`${content.showcase.copyLabel} ${content.showcase.responseHeading}`}
        />
      </div>
      <pre className="max-h-96 overflow-auto rounded-lg border border-zinc-200 bg-zinc-900 p-4 text-xs leading-relaxed text-zinc-100">
        <code>{API_EXAMPLE_RESPONSE_TEXT}</code>
      </pre>
    </section>
  );
}
