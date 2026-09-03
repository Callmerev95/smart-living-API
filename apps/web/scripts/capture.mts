/**
 * Pengambil aset visual untuk README (`T-P6-08`).
 *
 * Dijalankan manual, bukan bagian dari `pnpm e2e`:
 *
 *   pnpm capture                                    # dari production
 *   CAPTURE_BASE_URL=http://localhost:3000 pnpm capture
 *
 * Kenapa script, bukan screenshot manual: ukuran dan framing konsisten antar
 * gambar, tidak ada elemen browser atau informasi pribadi yang ikut terekam, dan
 * bisa diulang identik ketika UI berubah.
 *
 * Locator diambil dari `content.ts` supaya script ikut berubah bersama copy —
 * pola yang sama dipakai `e2e/recommendations.spec.ts`.
 *
 * Frame GIF disimpan sebagai PNG terpisah, lalu digabung `scripts/make_gif.py`.
 * ffmpeg bawaan Playwright tidak punya encoder GIF (hanya `png` dan `libvpx`),
 * jadi merekam video tidak menolong.
 */
import { mkdir, rm } from "node:fs/promises";
import { join } from "node:path";

import { chromium, type Locator, type Page } from "@playwright/test";

import { content } from "../lib/constants/content.ts";

const BASE_URL = process.env.CAPTURE_BASE_URL ?? "https://smart-living-web-silk.vercel.app";
const ASSETS_DIR = join(process.cwd(), "..", "..", "docs", "assets");
const FRAMES_DIR = join(ASSETS_DIR, ".frames");

/** Retina agar teks tetap tajam saat GitHub menampilkannya lebih kecil. */
const VIEWPORT = { width: 1280, height: 800 };
const SCALE = 2;

const SEARCH_QUERY = "telur, ayam, wortel";
const UNKNOWN_QUERY = "telur, kangkung";

let frameIndex = 0;

/** Simpan satu frame GIF dengan nomor urut agar mudah diurutkan. */
async function frame(page: Page): Promise<void> {
  const name = String(frameIndex).padStart(3, "0");
  frameIndex += 1;
  await page.screenshot({ path: join(FRAMES_DIR, `${name}.png`) });
}

/**
 * Tunggu elemen benar-benar tampil sebelum capture.
 *
 * Tanpa ini screenshot bisa menangkap skeleton loading, bukan hasil akhir.
 */
async function waitVisible(locator: Locator): Promise<void> {
  await locator.first().waitFor({ state: "visible", timeout: 30_000 });
}

async function ingredientField(page: Page): Promise<Locator> {
  return page.getByLabel(content.input.label);
}

async function submit(page: Page): Promise<void> {
  await page.getByRole("button", { name: content.input.submit }).click();
}

/** Screenshot penuh viewport — header dan footer ikut, memberi konteks halaman. */
async function shot(page: Page, name: string): Promise<void> {
  await page.screenshot({ path: join(ASSETS_DIR, `${name}.png`) });
  console.log(`  ${name}.png`);
}

/**
 * Screenshot satu section.
 *
 * Dipakai untuk bagian yang lebih tinggi dari viewport (daftar hasil, showcase)
 * supaya isinya tidak terpotong.
 *
 * Header di aplikasi ini `sticky top-0 z-40`, sehingga saat Playwright men-scroll
 * untuk menangkap element yang panjang, header ikut menutupi baris pertama section
 * — heading hasil hilang di balik lapisan blur. Header dibuat `static` sementara
 * agar tidak lagi overlay; header tetap terlihat utuh di `home.png` dan
 * `detail.png` yang memotret viewport.
 */
async function shotSection(page: Page, locator: Locator, name: string): Promise<void> {
  const unstick = await page.addStyleTag({
    content: "header{position:static !important;}",
  });

  try {
    await locator.scrollIntoViewIfNeeded();
    // Beri jeda agar animasi scroll selesai sebelum shutter.
    await page.waitForTimeout(400);
    await locator.screenshot({ path: join(ASSETS_DIR, `${name}.png`) });
    console.log(`  ${name}.png`);
  } finally {
    // `parentNode.removeChild` dipakai karena handle-nya bertipe `Node`, yang
    // tidak punya `remove()`.
    await unstick.evaluate((node) => node.parentNode?.removeChild(node));
  }
}

async function main(): Promise<void> {
  console.log(`Capture dari ${BASE_URL}`);

  await mkdir(ASSETS_DIR, { recursive: true });
  await rm(FRAMES_DIR, { recursive: true, force: true });
  await mkdir(FRAMES_DIR, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: SCALE,
    // Kunci locale/timezone supaya hasil tidak bergantung mesin yang menjalankan.
    locale: "id-ID",
    timezoneId: "Asia/Jakarta",
    colorScheme: "light",
  });
  const page = await context.newPage();

  try {
    // --- 1. Halaman awal -----------------------------------------------------
    await page.goto(BASE_URL, { waitUntil: "networkidle" });
    await waitVisible(page.getByText(content.results.initial.title));
    await shot(page, "home");
    await frame(page);

    // --- GIF: mengetik bahan bertahap ---------------------------------------
    const field = await ingredientField(page);
    await field.click();
    for (const chunk of ["telur", ", ayam", ", wortel"]) {
      await field.type(chunk, { delay: 45 });
      await frame(page);
    }

    // --- 2. Hasil rekomendasi ------------------------------------------------
    await submit(page);
    await waitVisible(page.getByText(content.results.success.sortNote));
    // Kartu terakhir ikut ter-render sebelum section dipotret.
    await page.getByRole("link", { name: content.card.cta }).last().waitFor({ state: "visible" });
    await frame(page);

    const resultsSection = page.getByRole("region", { name: content.results.sectionLabel });
    await shotSection(page, resultsSection, "results");

    // --- 3. Detail resep -----------------------------------------------------
    await page.getByRole("link", { name: content.card.cta }).first().click();
    await waitVisible(page.getByRole("heading", { name: content.detail.stepsHeading }));
    await page.waitForTimeout(300);
    await shot(page, "detail");
    await frame(page);

    // --- 4. Bahan tak dikenali (Contract Delta v1.1) -------------------------
    await page.getByRole("link", { name: content.detail.back }).click();
    await waitVisible(page.getByText(content.results.initial.title));

    const fieldAgain = await ingredientField(page);
    await fieldAgain.fill(UNKNOWN_QUERY);
    await submit(page);
    await waitVisible(page.getByText(content.chip.unknownSuffix));
    await page.getByRole("link", { name: content.card.cta }).last().waitFor({ state: "visible" });

    const unknownSection = page.getByRole("region", { name: content.results.sectionLabel });
    await shotSection(page, unknownSection, "unknown");

    // --- 5. API showcase -----------------------------------------------------
    await fieldAgain.fill(SEARCH_QUERY);
    await submit(page);
    await waitVisible(page.getByText(content.results.success.sortNote));

    const showcaseHeading = page.getByRole("heading", { name: content.showcase.heading });
    await waitVisible(showcaseHeading);
    // Section showcase adalah induk heading-nya.
    const showcase = page.locator("section", { has: showcaseHeading });
    await shotSection(page, showcase.last(), "showcase");

        // 1 awal + 3 mengetik + 1 hasil + 1 detail = 6 frame.
    console.log(`\n${frameIndex} frame GIF di ${FRAMES_DIR}`);
    console.log("Lanjut: uv run --with pillow python scripts/make_gif.py");
  } finally {
    await context.close();
    await browser.close();
  }
}

await main();
