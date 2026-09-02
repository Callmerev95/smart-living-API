import { Badge } from "@/components/ui/Badge";
import { content, fill, matchTier, type MatchTier } from "@/lib/constants/content";

const tones: Record<MatchTier, "success" | "info" | "warning" | "neutral"> = {
  perfect: "success",
  high: "info",
  medium: "warning",
  low: "neutral",
};

/**
 * Badge persentase kecocokan dengan tier visual (`docs/content-schema.md` §B.6.2).
 *
 * Tier ditentukan oleh fungsi murni `matchTier`, bukan ternary bertumpuk di JSX.
 * Informasi tier tidak hanya lewat warna — label teks selalu ada.
 */
export function MatchBadge({ percentage }: { percentage: number }) {
  const tier = matchTier(percentage);

  return (
    <span className="inline-flex flex-wrap items-center gap-2">
      <Badge tone={tones[tier]}>{fill(content.card.matchLabel, { percentage })}</Badge>
      <span className="text-xs text-zinc-500">{content.card.tier[tier]}</span>
    </span>
  );
}
