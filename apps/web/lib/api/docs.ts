/**
 * URL dokumentasi OpenAPI, dibangun dari base URL API — tidak hardcode.
 * Dipakai header dan showcase ("Di balik layar").
 */
export function getDocsUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
  return `${base.replace(/\/$/, "")}/docs`;
}
