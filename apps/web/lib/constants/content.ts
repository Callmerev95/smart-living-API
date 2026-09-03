/**
 * Seluruh copy user-facing — sumber tunggal dari `docs/content-schema.md` Bagian B.
 * Jangan menulis string literal di JSX; ubah di sini saja (§B.12).
 */

export const content = {
  ui: {
    loadingLabel: "Memuat",
  },

  brand: {
    name: "Smart Living",
    navLabel: "Navigasi utama",
    nav: {
      docs: "API Docs",
      repo: "GitHub",
    },
    skipToContent: "Lompat ke konten utama",
  },

  hero: {
    title: "Apa yang bisa saya masak dari bahan yang sudah ada?",
    subtitle:
      "Masukkan bahan yang ada di kulkas, dapatkan ide masakan yang benar-benar bisa kamu buat hari ini.",
    badge: "API-first · Deterministic matching",
  },

  input: {
    label: "Bahan yang kamu punya",
    placeholder: "telur, ayam, wortel",
    helper: "Pisahkan dengan koma. Boleh bahasa Indonesia atau Inggris.",
    submit: "Cari Resep",
    submitLoading: "Mencari…",
    clear: "Hapus semua",
    exampleLabel: "Coba contoh:",
    examples: ["telur, ayam, wortel", "tahu, tempe, kecap", "nasi, telur, bawang putih"],
    validation: {
      empty: "Tambahkan setidaknya satu bahan untuk mencari resep.",
      tooMany: "Maksimal {max} bahan per pencarian.",
      tooLong: "Nama bahan terlalu panjang.",
    },
  },

  chip: {
    unknownSuffix: "tidak dikenali",
    unknownTooltip:
      "Bahan ini belum ada di kamus kami, jadi tidak dipakai saat mencari resep.",
    normalizedTooltip: "Kami mengenali bahan ini sebagai {displayName}.",
  },

  results: {
    chipsLabel: "Bahan yang dicari",
    sectionLabel: "Rekomendasi",
    initial: {
      title: "Mulai dari bahan yang ada",
      body: "Masukkan minimal satu bahan, lalu kami tunjukkan masakan yang paling mungkin kamu buat.",
    },
    loading: {
      label: "Mencocokkan bahan dengan resep…",
    },
    success: {
      heading: "{count} resep cocok untuk bahanmu",
      headingSingle: "1 resep cocok untuk bahanmu",
      sortNote: "Diurutkan dari yang paling cocok.",
    },
    empty: {
      title: "Belum ada resep yang cukup cocok",
      body: "Kami tidak menemukan kecocokan yang kuat. Coba tambah satu atau dua bahan lagi.",
      cta: "Tambah bahan",
    },
    allUnknown: {
      title: "Bahan belum ada di kamus kami",
      body: "Kami belum mengenali {list}. Coba tulis dengan nama yang lebih umum, misalnya \"telur\" atau \"ayam\".",
    },
    error: {
      title: "Gagal mengambil rekomendasi",
      body: "Terjadi masalah saat menghubungi server. Coba lagi sebentar.",
      retry: "Coba lagi",
    },
  },

  card: {
    matchLabel: "{percentage}% cocok",
    availableLabel: "Sudah ada",
    missingLabel: "Perlu dibeli",
    missingEmpty: "Semua bahan utama sudah ada",
    timeLabel: "{minutes} menit",
    servingsLabel: "{servings} porsi",
    cta: "Lihat Resep",
    tier: {
      perfect: "Semua bahan utama ada",
      high: "Hampir lengkap",
      medium: "Perlu beberapa bahan",
      low: "Perlu banyak bahan",
    },
    difficulty: {
      easy: "Mudah",
      medium: "Sedang",
      hard: "Sulit",
    } as Record<string, string>,
  },

  detail: {
    ingredientsHeading: "Bahan",
    stepsHeading: "Cara Membuat",
    metaHeading: "Informasi",
    stapleNote:
      "Bahan pokok seperti garam dan minyak dianggap sudah tersedia.",
    optionalSuffix: "(opsional)",
    back: "Kembali ke hasil",
    notFound: {
      title: "Resep tidak ditemukan",
      body: "Resep yang kamu cari tidak ada atau sudah dihapus.",
    },
    loading: "Memuat resep…",
  },

  errors: {
    INVALID_INGREDIENTS: "Tambahkan setidaknya satu bahan untuk mencari resep.",
    VALIDATION_ERROR: "Ada input yang belum sesuai. Periksa kembali bahan yang kamu masukkan.",
    RECIPE_NOT_FOUND: "Resep tidak ditemukan.",
    INGREDIENT_NOT_FOUND: "Bahan tidak ditemukan.",
    INTERNAL_ERROR: "Ada masalah di sisi kami. Coba lagi sebentar.",
    network: "Tidak bisa menghubungi server. Periksa koneksi kamu.",
    unknown: "Terjadi kesalahan. Coba lagi.",
  },

  footer: {
    tagline: "Mengubah bahan sisa menjadi keputusan memasak.",
    repoLabel: "Lihat di GitHub",
  },

  showcase: {
    eyebrow: "Untuk developer",
    heading: "Di balik layar",
    subheading: "Frontend ini hanya salah satu client dari Smart Living API.",
    requestHeading: "Contoh Request",
    responseHeading: "Contoh Response",
    architectureHeading: "Arsitektur",
    stackHeading: "Tech Stack",
    decisionsHeading: "Keputusan Teknis",
    docsLabel: "Buka dokumentasi OpenAPI",
    copyLabel: "Copy",
    copiedLabel: "Tersalin",
    diagramAlt:
      "Alur permintaan: browser memanggil Next.js, Next.js memanggil Smart Living API, " +
      "API menormalisasi bahan lalu menghitung kecocokan dan mengurutkan hasil, " +
      "data resep dibaca dari berkas JSON lewat repository.",
    diagramFlow: [
      { label: "Browser", note: "Input bahan dari pengguna" },
      { label: "Next.js (Web)", note: "Client API, bukan tempat business logic" },
      { label: "Smart Living API (FastAPI)", note: "Validasi request dan response" },
      { label: "Ingredient Normalizer", note: "Teks bebas menjadi nama kanonik" },
      { label: "Matching Engine", note: "Hitung persentase kecocokan" },
      { label: "Ranking", note: "Urutkan deterministik dengan tie-breaker" },
      { label: "Recipe Repository", note: "Baca recipes.json sekali saat startup" },
    ],
    stack: [
      { layer: "Frontend", items: "Next.js, TypeScript, Tailwind CSS" },
      { layer: "Backend", items: "Python 3.12, FastAPI, Pydantic v2" },
      { layer: "Data", items: "JSON (version-controlled), PostgreSQL-ready" },
      { layer: "Testing", items: "pytest, Vitest, Playwright" },
      { layer: "Tooling", items: "uv, pnpm, ruff, Docker, GitHub Actions" },
    ],
    decisions: [
      {
        title: "Kenapa deterministik, bukan LLM?",
        body:
          "Ranking resep harus konsisten, murah, dan bisa dijelaskan. Input yang sama " +
          "selalu menghasilkan urutan yang sama. AI ditempatkan sebagai lapisan " +
          "enhancement, bukan fondasi. Trade-off-nya: input bahasa natural yang rumit " +
          "belum bisa dipahami.",
      },
      {
        title: "Kenapa garam dan minyak tidak dihitung?",
        body:
          "Bahan pokok dapur dianggap selalu tersedia, sehingga persentase kecocokan " +
          "mencerminkan bahan yang benar-benar menentukan. Trade-off-nya: asumsi ini " +
          "bisa salah untuk dapur yang benar-benar kosong.",
      },
      {
        title: "Kenapa JSON, bukan database?",
        body:
          "Untuk 60 resep, JSON version-controlled lebih cepat di-review dan tidak butuh " +
          "setup. Repository abstraction membuat migrasi ke PostgreSQL tidak mengubah " +
          "business logic. Trade-off-nya: query kompleks dan filter dinamis belum bisa.",
      },
    ],
  },

  meta: {
    title: "Smart Living — Masak dari bahan yang sudah ada",
    description:
      "Masukkan bahan yang ada di kulkas, dapatkan rekomendasi masakan yang bisa langsung kamu buat. API-first, deterministic matching.",
    ogTitle: "Smart Living",
    // Judul halaman detail: `{name} — Smart Living`.
    detailTitle: "{name} — Smart Living",
  },
} as const;

/**
 * Interpolasi placeholder `{key}` dari template content.
 * Contoh: `fill(content.results.success.heading, { count: 5 })`
 */
export function fill(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) =>
    key in values ? String(values[key]) : match,
  );
}

/** Batas input dari kontrak API (`docs/content-schema.md` §A.7). */
export const INPUT_LIMITS = {
  maxIngredients: 30,
  maxNameLength: 60,
} as const;

/** Tier visual persentase kecocokan (`docs/content-schema.md` §B.6.2). */
export type MatchTier = "perfect" | "high" | "medium" | "low";

export function matchTier(percentage: number): MatchTier {
  if (percentage >= 100) return "perfect";
  if (percentage >= 70) return "high";
  if (percentage >= 50) return "medium";
  return "low";
}
