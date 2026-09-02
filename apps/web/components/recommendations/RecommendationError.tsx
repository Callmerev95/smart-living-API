"use client";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { content } from "@/lib/constants/content";

export function RecommendationError({
  onRetry,
}: {
  onRetry: () => void;
}) {
  return (
    <Alert
      tone="error"
      title={content.results.error.title}
      action={<Button onClick={onRetry}>{content.results.error.retry}</Button>}
    >
      {content.results.error.body}
    </Alert>
  );
}
