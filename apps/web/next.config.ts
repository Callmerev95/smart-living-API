import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // `output: "standalone"` hanya untuk Docker (image ramping: server.js + node_modules
  // hasil trace). Di Vercel tracing ditangani platform sendiri, dan `.next/*.nft.json`
  // tidak dihasilkan — memaksakan standalone di Vercel membuat `next build` crash saat
  // `copyTracedFiles` membaca file yang tidak ada. `VERCEL` diset otomatis di Vercel.
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
