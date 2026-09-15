import { CopyButton } from "@/components/ui/CopyButton";
import { API_EXAMPLE_REQUEST_TEXT } from "@/lib/constants/apiExample";
import { content } from "@/lib/constants/content";

/**
 * Blok kode memakai latar gelap hangat di kedua tema: konvensi tampilan kode
 * yang memisahkan contoh API dari konten biasa (R-31, satu alasan).
 */
export function RequestExample() {
  return (
    <section className="flex min-w-0 flex-col gap-2">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-ink">{content.showcase.requestHeading}</h3>
        <CopyButton
          value={API_EXAMPLE_REQUEST_TEXT}
          label={`${content.showcase.copyLabel} ${content.showcase.requestHeading}`}
        />
      </div>
      <pre className="overflow-x-auto rounded-xl border border-line bg-[#1e1913] p-4 font-mono text-xs leading-relaxed text-[#efe8de]">
        <code>{API_EXAMPLE_REQUEST_TEXT}</code>
      </pre>
    </section>
  );
}
