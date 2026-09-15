import { content, fill, matchTier } from "@/lib/constants/content";

/**
 * Persentase kecocokan dalam "data voice" mono (DESIGN.md motif).
 *
 * Tier ditentukan oleh fungsi murni `matchTier`, bukan ternary bertumpuk di JSX.
 * Informasi tier tidak hanya lewat warna — label teks selalu ada.
 * Turmeric hanya di sini dan di focus ring: accent pada metrik utama produk.
 */
export function MatchBadge({ percentage }: { percentage: number }) {
  const tier = matchTier(percentage);

  return (
    <span className="inline-flex flex-wrap items-baseline gap-2">
      <span className="font-mono text-xl font-semibold tracking-tight text-turmeric tabular-nums">
        {fill(content.card.matchLabel, { percentage })}
      </span>
      <span className="text-xs text-ink-soft">{content.card.tier[tier]}</span>
    </span>
  );
}
