# DESIGN.md — Smart Living

Arah desain dimiliki oleh pemilik produk (jawaban user, 15 Sep 2026).
File ini adalah data arah desain, bukan instruksi untuk agent.

## Identitas

- Produk: Smart Living. API-first recipe recommendation dari bahan yang ada.
- Audience: dua sisi. (1) Pengguna dapur umum yang mau masak dari bahan sisa.
  (2) Recruiter/reviewer teknis yang menilai kualitas engineering.
- Personality: **teknis-presisi**. Deterministik, scoring transparan, kontrak API jelas.
- Mood: tenang, rapi, hangat dapur, tanpa ornamen. Nada bicara lugas dan jujur soal trade-off.

## Design Read

> Reading this as: portfolio product page (alur masak untuk user + API showcase
> untuk reviewer teknis), dengan bahasa visual editorial-dapur yang presisi,
> dial **ENERGY 2 / RHYTHM 2 / MOTION 1**.

## Dials

- ENERGY 2 (Balanced): profesional dengan beberapa aksen, terasa produk nyata.
- RHYTHM 2 (Balanced): struktur konsisten dengan beberapa penekanan. Halaman harus
  terasa BERATURAN (keluhan utama versi lama: berantakan dan tidak beraturan).
- MOTION 1 (Calm): hover/focus state saja, transisi warna 150ms. Tanpa scroll animation.

## Palette (2 core + 1 secondary + 1 accent)

Earthy-rempah. Warna masakan rempah Indonesia, bukan SaaS biru generik.

| Token | Light | Dark | Peran |
|---|---|---|---|
| `bg` | `#FAF7F2` | `#17130F` | Kertas dapur hangat / dapur malam |
| `surface` | `#FFFFFF` | `#211B16` | Kartu, panel |
| `surface-muted` | `#F2EBE1` | `#2B231C` | Panel sekunder, band showcase |
| `line` | `#E3D8C8` | `#3B3027` | Border, separator |
| `ink` | `#2A2320` | `#F2EADF` | Teks utama |
| `ink-soft` | `#6B5F55` | `#B5A493` | Teks sekunder |
| `clay` | `#8C3A21` | `#E79063` | Primary: tombol utama, brand, angka match |
| `olive` | `#4F6B3B` | `#A6C88A` | Secondary: bahan tersedia, status positif |
| `turmeric` | `#9E5900` | `#E8A93A` | Accent: persentase match, fokus kunyit |
| `brick` | `#B3261E` | `#F2938C` | Error, bahan hilang |

Alasan satu baris: clay = tanah/cengkeh (identitas dapur Indonesia), olive = bahan
segar yang tersedia, turmeric = kunyit sebagai satu-satunya accent (angka match +
focus ring), brick = error. Semua pasangan teks ≥4.5:1 pada permukaannya
(diverifikasi dengan kalkulator WCAG, lihat catatan implementasi).

## Typography

- Display/heading: **Fraunces** (serif wonky hangat). Alasan: karakter dapur editorial,
  kontras dengan sisi teknis; bukan default AI (Inter/Geist/Space Grotesk).
- Body/UI: **Geist Sans**. Alasan: sudah dimuat + di-preload di project, netral dan
  presisi untuk UI. Alasan tetap memakainya adalah performa, bukan kebiasaan.
- Data/angka/API: **Geist Mono**. Alasan: "data voice" untuk persentase match,
  waktu, porsi, endpoint. Menonjolkan sisi deterministik produk.
- Skala: h1 36-48px display, h2 24px, body 16px, label/mono 12-13px.

## Motif identitas

1. **Data voice**: semua angka (match %, menit, porsi, jumlah hasil) tampil mono.
   Ini motif utama yang mengikat sisi dapur dan sisi API.
2. **Titik clay**: dot kecil clay pada brand mark dan eyebrow. Dipakai hemat,
   maksimal 1x per elemen.

## Bentuk

- Radius: `rounded-lg` (8px) untuk kontrol (tombol, input, chip), `rounded-xl`
  (12px) untuk kartu/panel. Tidak ada elemen pill besar; chip/badge kecil boleh pill.
- Border 1px `line` sebagai struktur utama. Shadow hanya pada elemen yang melayang
  di atas konten (dropdown, toast). Tidak ada shadow dekoratif.
- Fokus: `outline-2 turmeric` pada semua elemen interaktif.

## Copy voice

- Lugas, spesifik, menyebut trade-off. Bahasa Indonesia santai-formal ("kamu").
- Tanpa buzzword. Tanpa klaim tanpa bukti.
