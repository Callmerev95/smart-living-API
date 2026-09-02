/**
 * Audit otomatis untuk exit criteria Phase 5 (`docs/development-roadmap.md` §6.3).
 *
 * Test ini menjaga aturan yang mudah dilanggar tanpa sengaja saat menambah komponen:
 * copy harus dari `content.ts`, request harus lewat `lib/api/`, dan tidak ada URL
 * API yang hardcode.
 */
import { describe, expect, it } from "vitest";

const SOURCE_GLOBS = {
  components: import.meta.glob("../components/**/*.tsx", { query: "?raw", import: "default" }),
  app: import.meta.glob("../app/**/*.tsx", { query: "?raw", import: "default" }),
  hooks: import.meta.glob("../hooks/**/*.ts", { query: "?raw", import: "default" }),
  api: import.meta.glob("../lib/api/**/*.ts", { query: "?raw", import: "default" }),
};

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
