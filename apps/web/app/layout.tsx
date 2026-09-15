import type { Metadata } from "next";
import { Fraunces, Geist, Geist_Mono } from "next/font/google";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { content } from "@/lib/constants/content";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

/**
 * Display serif untuk heading (DESIGN.md). Hanya sumbu weight yang dimuat:
 * italic dan axis dekoratif tidak dipakai di mana pun.
 */
const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
});

/**
 * Base URL absolut untuk metadata sosial (`og:image` harus absolute supaya bisa
 * di-baca crawler). Prioritas: env eksplisit → domain deployment Vercel →
 * domain produksi. Tanpa ini Next.js mengeluarkan `og:image` relatif.
 */
const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ??
  (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : undefined);

/**
 * Setel tema sebelum render pertama agar tidak ada kedipan latar salah warna.
 * Prioritas: pilihan user di localStorage → preferensi OS. Script ini dipasang
 * sinkron di awal <body>; class `.dark` sudah ada sebelum konten terlihat.
 */
const themeScript = `(function(){try{var s=localStorage.getItem("sl-theme");var d=s?s==="dark":window.matchMedia("(prefers-color-scheme: dark)").matches;var el=document.documentElement;el.classList.toggle("dark",d);el.style.colorScheme=d?"dark":"light";}catch(e){}})();`;

export const metadata: Metadata = {
  ...(SITE_URL ? { metadataBase: new URL(SITE_URL) } : {}),
  title: content.meta.title,
  description: content.meta.description,
  openGraph: {
    title: content.meta.ogTitle,
    description: content.meta.description,
    type: "website",
    siteName: content.brand.name,
    images: [{ url: "/opengraph-image", width: 1200, height: 630, alt: content.meta.ogTitle }],
  },
  twitter: {
    card: "summary_large_image",
    title: content.meta.ogTitle,
    description: content.meta.description,
    images: ["/opengraph-image"],
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="id"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} ${fraunces.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-bg text-ink">
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-surface focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-ink focus:shadow"
        >
          {content.brand.skipToContent}
        </a>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
