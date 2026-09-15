import { CopyButton } from "@/components/ui/CopyButton";
import { API_EXAMPLE_RESPONSE_TEXT } from "@/lib/constants/apiExample";
import { content } from "@/lib/constants/content";

/**
 * Response dibatasi tingginya (max-h) dengan fade di tepi bawah sebagai isyarat
 * bahwa konten berlanjut; tanpa itu, scrollbar tipis adalah satu-satunya petunjuk.
 * Blok kode memakai latar gelap hangat di kedua tema (konvensi tampilan kode).
 */
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
      <div className="relative">
        <pre className="max-h-[28rem] overflow-auto rounded-xl border border-line bg-[#1e1913] p-4 font-mono text-xs leading-relaxed text-[#efe8de]">
          <code>{API_EXAMPLE_RESPONSE_TEXT}</code>
        </pre>
        <span
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-1 bottom-1 h-10 rounded-b-xl bg-gradient-to-t from-[#1e1913] via-[#1e1913]/70 to-transparent"
        />
      </div>
    </section>
  );
}
