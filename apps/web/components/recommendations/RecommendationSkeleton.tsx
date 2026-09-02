import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { content } from "@/lib/constants/content";

/**
 * Placeholder saat request berjalan (`docs/component-architecture.md` §30).
 *
 * Skeleton disembunyikan dari screen reader; status pemuatan diumumkan satu kali
 * lewat teks visually-hidden, bukan diulang per placeholder.
 */
export function RecommendationSkeleton() {
  return (
    <div>
      <p className="sr-only" role="status">
        {content.results.loading.label}
      </p>
      <div aria-hidden="true" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[0, 1, 2].map((index) => (
          <Card key={index} className="flex flex-col gap-3">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-8 w-28" />
          </Card>
        ))}
      </div>
    </div>
  );
}
