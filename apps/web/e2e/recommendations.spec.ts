import { expect, test } from "@playwright/test";

import { content } from "../lib/constants/content";

const RECOMMENDATIONS_ROUTE = "**/api/v1/recommendations";

/** Isi input bahan lalu submit lewat tombol. */
async function search(page: import("@playwright/test").Page, ingredients: string) {
  await page.getByLabel(content.input.label).fill(ingredients);
  await page.getByRole("button", { name: content.input.submit }).click();
}

test.describe("alur utama", () => {
  test("input bahan menghasilkan kartu resep", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { level: 1 })).toHaveText(content.hero.title);
    await expect(page.getByText(content.results.initial.title)).toBeVisible();

    await search(page, "telur, ayam, wortel");

    // Heading hasil dan minimal satu kartu resep.
    await expect(page.getByText(content.results.success.sortNote)).toBeVisible();
    const cards = page.getByRole("link", { name: content.card.cta });
    expect(await cards.count()).toBeGreaterThan(0);
  });

  test("chip normalisasi menampilkan nama Indonesia (Delta 3)", async ({ page }) => {
    await page.goto("/");
    await search(page, "telur, ayam, wortel");

    const chips = page.getByLabel(content.results.chipsLabel);
    await expect(chips).toContainText("Telur");
    await expect(chips).toContainText("Ayam");
    await expect(chips).toContainText("Wortel");
  });

  test("membuka detail resep lalu kembali", async ({ page }) => {
    await page.goto("/");
    await search(page, "telur, ayam, wortel");

    await page.getByRole("link", { name: content.card.cta }).first().click();

    await expect(page).toHaveURL(/\/recipes\/recipe_\d{3}$/);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.getByRole("heading", { name: content.detail.ingredientsHeading })).toBeVisible();
    await expect(page.getByRole("heading", { name: content.detail.stepsHeading })).toBeVisible();
    // Transparansi Delta 1: user diberi tahu kenapa staple tidak dihitung.
    await expect(page.getByText(content.detail.stapleNote)).toBeVisible();

    await page.getByRole("link", { name: content.detail.back }).click();
    await expect(page).toHaveURL("/");
  });
});

test.describe("Contract Delta v1.1", () => {
  test("bahan tak dikenali ditandai tapi hasil tetap muncul (Delta 2)", async ({ page }) => {
    await page.goto("/");
    await search(page, "telur, kangkung");

    const chips = page.getByLabel(content.results.chipsLabel);
    await expect(chips).toContainText("kangkung");
    await expect(chips).toContainText(content.chip.unknownSuffix);

    // Bahan tak dikenal tidak menggagalkan pencarian.
    const cards = page.getByRole("link", { name: content.card.cta });
    expect(await cards.count()).toBeGreaterThan(0);
  });

  test("semua bahan tak dikenali menampilkan empty state khusus", async ({ page }) => {
    await page.goto("/");
    await search(page, "kangkung, durian");

    await expect(page.getByText(content.results.allUnknown.title)).toBeVisible();
    await expect(page.getByText(/kangkung, durian/)).toBeVisible();
  });
});

test.describe("validasi input", () => {
  test("input kosong tidak mengirim request ke API", async ({ page }) => {
    let requestCount = 0;
    await page.route(RECOMMENDATIONS_ROUTE, async (route) => {
      requestCount += 1;
      await route.continue();
    });

    await page.goto("/");
    await page.getByRole("button", { name: content.input.submit }).click();

    // Locator berbasis teks: `getByRole("alert")` juga menangkap route announcer
    // milik Next.js (`#__next-route-announcer__`).
    await expect(page.getByText(content.input.validation.empty)).toBeVisible();
    // Pesan error harus terhubung ke input secara aksesibel.
    await expect(page.getByLabel(content.input.label)).toHaveAttribute("aria-invalid", "true");
    expect(requestCount).toBe(0);
  });

  test("pesan validasi hilang setelah input valid", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: content.input.submit }).click();
    await expect(page.getByText(content.input.validation.empty)).toBeVisible();

    await search(page, "telur, ayam");

    await expect(page.getByText(content.input.validation.empty)).toBeHidden();
    await expect(page.getByLabel(content.input.label)).not.toHaveAttribute("aria-invalid", "true");
  });
});

test.describe("interaksi tambahan", () => {
  test("tombol contoh mengisi field lalu menghasilkan resep", async ({ page }) => {
    await page.goto("/");

    const example = content.input.examples[0];
    await page.getByRole("button", { name: example }).click();
    await expect(page.getByLabel(content.input.label)).toHaveValue(example);

    await page.getByRole("button", { name: content.input.submit }).click();
    await expect(page.getByText(content.results.success.sortNote)).toBeVisible();
  });

  test("alur bisa diselesaikan hanya dengan keyboard", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel(content.input.label).focus();
    await page.keyboard.type("telur, ayam, wortel");
    await page.keyboard.press("Enter");

    await expect(page.getByText(content.results.success.sortNote)).toBeVisible();
  });
});

test.describe("API showcase", () => {
  test("menampilkan contoh request, response, dan keputusan teknis", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: content.showcase.heading })).toBeVisible();
    await expect(page.getByText(content.showcase.requestHeading)).toBeVisible();
    await expect(page.getByText(content.showcase.responseHeading)).toBeVisible();
    await expect(page.getByText(content.showcase.decisionsHeading)).toBeVisible();

    const docsLink = page.getByRole("link", { name: content.showcase.docsLabel });
    await expect(docsLink).toHaveAttribute("href", /\/docs$/);
  });
});
