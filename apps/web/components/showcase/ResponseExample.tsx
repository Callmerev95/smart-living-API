import { CopyButton } from "@/components/ui/CopyButton";
import { API_EXAMPLE_RESPONSE_TEXT } from "@/lib/constants/apiExample";
import { content } from "@/lib/constants/content";

export function ResponseExample() {
  return (
    <section className="flex min-w-0 flex-col gap-2">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-ink">{content.showcase.responseHeading}</h3>
        <CopyButton
          value={API_EXAMPLE_RESPONSE_TEXT}
          label={`${content.showcase.copyLabel} ${content.showcase.responseHeading}`}
        />
      </div>
      <pre className="max-h-96 overflow-auto rounded-xl border border-line bg-[#1e1913] p-4 font-mono text-xs leading-relaxed text-[#efe8de]">
        <code>{API_EXAMPLE_RESPONSE_TEXT}</code>
      </pre>
    </section>
  );
}
