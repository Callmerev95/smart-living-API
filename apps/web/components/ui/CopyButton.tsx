"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { content } from "@/lib/constants/content";

/**
 * Tombol copy generik. Tidak tahu apa yang dicopy — pemanggil yang memberi label
 * agar screen reader tahu konteksnya.
 */
export function CopyButton({ value, label }: { value: string; label: string }) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(timer);
  }, [copied]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
    } catch {
      // Clipboard bisa ditolak (permission/insecure context). Diamkan — menyalin
      // adalah kenyamanan, bukan fungsi utama.
    }
  }

  return (
    <Button
      variant="secondary"
      className="px-2.5 py-1 text-xs"
      onClick={handleCopy}
      aria-label={label}
    >
      {copied ? content.showcase.copiedLabel : content.showcase.copyLabel}
    </Button>
  );
}
