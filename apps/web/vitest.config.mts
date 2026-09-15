import { defineConfig } from "vitest/config";
import { resolve } from "node:path";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.{ts,tsx}"],
    environmentOptions: {
      jsdom: {
        // localStorage jsdom hanya aktif dengan origin non-opaque (butuh toggle tema).
        url: "http://localhost:3000",
      },
    },
  },
  resolve: {
    alias: {
      "@": resolve(import.meta.dirname, "."),
    },
  },
});
