import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Node 22+ punya global `localStorage` eksperimental yang tidak berfungsi tanpa
// flag `--localstorage-file`, dan getter itu menutupi localStorage bawaan jsdom
// di environment test. Polyfill in-memory agar toggle tema bisa diuji.
if (typeof window !== "undefined" && !window.localStorage) {
  const store = new Map<string, string>();
  Object.defineProperty(window, "localStorage", {
    configurable: true,
    value: {
      getItem: (key: string) => (store.has(key) ? (store.get(key) as string) : null),
      setItem: (key: string, value: string) => {
        store.set(key, String(value));
      },
      removeItem: (key: string) => {
        store.delete(key);
      },
      clear: () => store.clear(),
      key: (index: number) => Array.from(store.keys())[index] ?? null,
      get length() {
        return store.size;
      },
    },
  });
}

// Auto-cleanup RTL hanya aktif bila global `afterEach` tersedia. Config Vitest di
// proyek ini tidak memakai `globals: true`, jadi cleanup dipasang manual — tanpa ini
// DOM menumpuk antar test dan query seperti getByRole menemukan elemen ganda.
afterEach(() => {
  cleanup();
});
