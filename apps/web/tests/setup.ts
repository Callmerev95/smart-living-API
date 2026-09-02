import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Auto-cleanup RTL hanya aktif bila global `afterEach` tersedia. Config Vitest di
// proyek ini tidak memakai `globals: true`, jadi cleanup dipasang manual — tanpa ini
// DOM menumpuk antar test dan query seperti getByRole menemukan elemen ganda.
afterEach(() => {
  cleanup();
});
