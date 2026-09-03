/**
 * Audit otomatis untuk exit criteria Phase 5 (`docs/development-roadmap.md` §6.3).
 *
 * Test ini menjaga aturan yang mudah dilanggar tanpa sengaja saat menambah komponen:
 * copy harus dari `content.ts`, request harus lewat `lib/api/`, dan tidak ada URL
 * API yang hardcode.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const SOURCE_GLOBS = {
  components: import.meta.glob("../components/**/*.tsx", { query: "?raw", import: "default" }),
  app: import.meta.glob("../app/**/*.tsx", { query: "?raw", import: "default" }),
  hooks: import.meta.glob("../hooks/**/*.ts", { query: "?raw", import: "default" }),
  api: import.meta.glob("../lib/api/**/*.ts", { query: "?raw", import: "default" }),
  config: import.meta.glob("../{next.config.ts,vercel.json}", {
    query: "?raw",
    import: "default",
  }),
};

/**
 * Baca berkas apa adanya dari disk.
 *
 * `import.meta.glob("?raw")` tidak bisa dipakai untuk CSS — Vite menangani CSS
 * lewat pipeline sendiri dan mengembalikan string kosong.
 */
function readProjectFile(relativePath: string): string {
  return readFileSync(join(process.cwd(), relativePath), "utf8");
}

async function loadSources(
  group: keyof typeof SOURCE_GLOBS,
): Promise<Array<[string, string]>> {
  const entries = Object.entries(SOURCE_GLOBS[group]);
  return Promise.all(
    entries.map(async ([path, loader]) => [path, (await loader()) as string] as [string, string]),
  );
}

/** Buang komentar dan docstring agar audit hanya melihat kode nyata. */
function stripComments(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
}

describe("audit copy (§B.12)", () => {
  it("tidak ada atribut teks berbahasa Indonesia yang hardcode di JSX", async () => {
    const sources = [...(await loadSources("components")), ...(await loadSources("app"))];
    const offenders: string[] = [];

    for (const [path, raw] of sources) {
      const code = stripComments(raw);
      // aria-label / placeholder / title dengan literal string, bukan ekspresi.
      const matches = code.match(/(aria-label|placeholder|title)="[^"]+"/g) ?? [];
      for (const match of matches) {
        offenders.push(`${path}: ${match}`);
      }
    }

    expect(offenders).toEqual([]);
  });

  it("semua komponen presentasi mengimpor copy dari content.ts", async () => {
    const sources = await loadSources("components");
    // Komponen yang memang tidak punya copy sendiri.
    const exempt = ["Card.tsx", "Skeleton.tsx", "Badge.tsx"];

    const offenders: string[] = [];
    for (const [path, raw] of sources) {
      if (exempt.some((name) => path.endsWith(name))) continue;

      const code = stripComments(raw);
      // Deteksi teks Indonesia di dalam JSX text node.
      const hasIndonesianText = />\s*[A-Z][a-z]+\s+[a-z]+/.test(code);
      const importsContent = code.includes('from "@/lib/constants/content"');

      if (hasIndonesianText && !importsContent) {
        offenders.push(path);
      }
    }

    expect(offenders).toEqual([]);
  });
});

describe("audit boundary API (§11)", () => {
  it("hanya lib/api yang memanggil fetch", async () => {
    const sources = [
      ...(await loadSources("components")),
      ...(await loadSources("app")),
      ...(await loadSources("hooks")),
    ];

    const offenders = sources
      .filter(([, raw]) => stripComments(raw).includes("fetch("))
      .map(([path]) => path);

    expect(offenders).toEqual([]);
  });

  it("tidak ada URL API hardcode di luar lib/api", async () => {
    const sources = [
      ...(await loadSources("components")),
      ...(await loadSources("app")),
      ...(await loadSources("hooks")),
    ];

    const offenders: string[] = [];
    for (const [path, raw] of sources) {
      const code = stripComments(raw);
      if (/localhost:\d+|127\.0\.0\.1|\/api\/v1/.test(code)) {
        offenders.push(path);
      }
    }

    expect(offenders).toEqual([]);
  });

  it("base URL dibaca dari env, bukan konstanta", async () => {
    const sources = await loadSources("api");
    const client = sources.find(([path]) => path.endsWith("client.ts"));

    expect(client).toBeDefined();
    expect(client?.[1]).toContain("NEXT_PUBLIC_API_BASE_URL");
  });
});

describe("audit deployment config", () => {
  it("vercel.json menyatakan framework nextjs", async () => {
    const sources = await loadSources("config");
    const vc = sources.find(([path]) => path.endsWith("vercel.json"));
    expect(vc).toBeDefined();
    expect(vc![1]).toContain('"nextjs"');
  });

  it("output standalone conditional pada VERCEL env", async () => {
    const sources = await loadSources("config");
    const cfg = sources.find(([path]) => path.endsWith("next.config.ts"));
    expect(cfg).toBeDefined();
    const code = cfg![1];
    expect(code).toContain("process.env.VERCEL");
    expect(code).toContain("undefined : \"standalone\"");
    // Tidak ada hardcode `output: "standalone"` tanpa guard.
    expect(code).not.toMatch(/^\s*output:\s*"standalone"/m);
  });
});

describe("audit branding & metadata", () => {
  it("body memakai font yang dimuat, bukan Arial", () => {
    // Komentar aturan sebelumnya menyebut "Arial"; buang agar cek hanya kode nyata.
    const css = stripComments(readProjectFile("app/globals.css"));

    // Font Geist di-preload di layout; memakai Arial membuat preload itu terbuang.
    expect(css).not.toContain("Arial");
    expect(css).toContain("var(--font-sans)");
  });

  it("tidak ada blok dark mode yang bertentangan dengan latar terang", () => {
    const css = readProjectFile("app/globals.css");

    // `prefers-color-scheme: dark` pernah menyetel --foreground terang sementara
    // body tetap bg-zinc-50, sehingga teks nyaris tak terbaca.
    expect(css).not.toContain("prefers-color-scheme");
  });

  it("layout menyediakan metadata Open Graph dan Twitter lengkap", async () => {
    const sources = await loadSources("app");
    const layout = sources.find(([path]) => path.endsWith("layout.tsx"));

    expect(layout).toBeDefined();
    const code = layout![1];
    for (const field of ["openGraph", "twitter", "summary_large_image", "opengraph-image"]) {
      expect(code, field).toContain(field);
    }
  });

  it("og:image absolute lewat metadataBase dari env/deployment", async () => {
    const sources = await loadSources("app");
    const layout = sources.find(([path]) => path.endsWith("layout.tsx"));

    expect(layout).toBeDefined();
    const code = layout![1];
    expect(code).toContain("metadataBase");
    expect(code).toContain("VERCEL_URL");
  });

  it("OG image digenerate lewat ImageResponse, bukan aset statis", async () => {
    const sources = await loadSources("app");
    const og = sources.find(([path]) => path.endsWith("opengraph-image.tsx"));

    expect(og).toBeDefined();
    expect(og![1]).toContain("ImageResponse");
    expect(og![1]).toContain("next/og");
    // Satori hanya mendukung flexbox.
    expect(og![1]).not.toContain("display: \"grid\"");
  });

  it("judul halaman detail memakai nama resep, bukan ID", async () => {
    const sources = await loadSources("app");
    const page = sources.find(([path]) => path.includes("recipes/[id]"));

    expect(page).toBeDefined();
    const code = page![1];
    expect(code).toContain("getRecipe");
    expect(code).toContain("content.meta.detailTitle");
  });

  it("header memakai copy dari content.ts dan URL docs dari env", async () => {
    const sources = await loadSources("components");
    const header = sources.find(([path]) => path.endsWith("Header.tsx"));

    expect(header).toBeDefined();
    expect(header![1]).toContain('from "@/lib/constants/content"');
    expect(header![1]).toContain("getDocsUrl");
  });

  it("setiap halaman punya anchor #main-content untuk skip link", async () => {
    const sources = await loadSources("app");
    const pages = sources.filter(([path]) => path.endsWith("page.tsx"));

    expect(pages.length).toBeGreaterThan(0);
    for (const [path, raw] of pages) {
      expect(raw, path).toContain('id="main-content"');
    }
  });

  it("link eksternal target=_blank selalu punya rel noopener", async () => {
    const sources = await loadSources("components");

    for (const [path, raw] of sources) {
      const code = stripComments(raw);
      if (!code.includes('target="_blank"')) continue;
      expect(code, path).toContain("noopener");
    }
  });
});

describe("audit aksesibilitas (§6.3)", () => {
  it("skeleton disembunyikan dari screen reader", async () => {
    const sources = await loadSources("components");
    const skeleton = sources.find(([path]) => path.endsWith("RecommendationSkeleton.tsx"));

    expect(skeleton?.[1]).toContain('aria-hidden="true"');
  });

  it("hasil rekomendasi diumumkan lewat role status", async () => {
    const sources = await loadSources("components");
    const section = sources.find(([path]) => path.endsWith("RecommendationSection.tsx"));

    expect(section?.[1]).toContain('role="status"');
  });

  it("focus ring tidak dihapus pada elemen interaktif", async () => {
    const sources = await loadSources("components");
    const primitives = sources.filter(([path]) =>
      ["ui/Button.tsx", "ui/Input.tsx"].some((name) => path.endsWith(name)),
    );

    expect(primitives).toHaveLength(2);
    for (const [path, raw] of primitives) {
      expect(raw, path).toContain("focus-visible:outline");
    }

    // Tidak ada komponen mana pun yang mematikan outline fokus.
    for (const [path, raw] of sources) {
      expect(raw, path).not.toContain("outline-none");
    }
  });

  it("input punya label terasosiasi lewat htmlFor", async () => {
    const sources = await loadSources("components");
    const input = sources.find(([path]) => path.endsWith("ui/Input.tsx"));

    expect(input?.[1]).toContain("htmlFor");
  });

  it("pembeda status tidak hanya lewat warna", async () => {
    const sources = await loadSources("components");

    const tag = sources.find(([path]) => path.endsWith("IngredientTag.tsx"));
    expect(tag?.[1]).toContain("unknownSuffix");
    expect(tag?.[1]).toContain("border-dashed");

    const badge = sources.find(([path]) => path.endsWith("MatchBadge.tsx"));
    expect(badge?.[1]).toContain("content.card.tier");

    const card = sources.find(([path]) => path.endsWith("RecommendationCard.tsx"));
    expect(card?.[1]).toContain("availableLabel");
    expect(card?.[1]).toContain("missingLabel");
  });
});
