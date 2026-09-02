import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Menghasilkan `.next/standalone` (server.js + node_modules hasil trace) sehingga
  // image Docker web ramping. Tanpa ini, image harus membawa seluruh node_modules.
  output: "standalone",
};

export default nextConfig;
