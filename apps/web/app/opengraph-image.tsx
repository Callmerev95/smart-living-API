import { ImageResponse } from "next/og";

import { content } from "@/lib/constants/content";

/**
 * Open Graph image (`app/opengraph-image` file convention).
 *
 * Digenerate dari kode, bukan berkas PNG statis, supaya copy-nya selalu ikut
 * `content.ts` dan tidak ada aset yang perlu dipelihara terpisah. Next.js
 * menyuntikkan `og:image` beserta ukuran dan alt-nya ke `<head>` otomatis.
 *
 * Satori (mesin di balik `ImageResponse`) hanya mendukung flexbox — hindari
 * `display: grid` di sini.
 */
export const alt = content.meta.ogTitle;

export const size = { width: 1200, height: 630 };

export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          backgroundColor: "#fffbeb",
          backgroundImage:
            "linear-gradient(135deg, #fffbeb 0%, #fef3c7 55%, #fde68a 100%)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              backgroundColor: "#f59e0b",
            }}
          />
          <div style={{ fontSize: 34, fontWeight: 600, color: "#78350f" }}>
            {content.brand.name}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div
            style={{
              fontSize: 62,
              fontWeight: 700,
              lineHeight: 1.15,
              color: "#18181b",
            }}
          >
            {content.hero.title}
          </div>
          <div style={{ fontSize: 30, color: "#52525b", lineHeight: 1.35 }}>
            {content.hero.subtitle}
          </div>
        </div>

        <div style={{ fontSize: 26, color: "#92400e", fontWeight: 500 }}>
          {content.hero.badge}
        </div>
      </div>
    ),
    size,
  );
}
