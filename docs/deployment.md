# Panduan Deployment

Web ke **Vercel**, API ke **Railway** lewat Dockerfile.

Pemilihan platform sengaja dipisah: Vercel memberi edge network dan preview deployment
untuk Next.js, sementara Railway menjalankan `docker/api.Dockerfile` yang sama dengan yang
diverifikasi CI. Dockerfile-nya bukan pajangan — ia yang menjalankan API production.

---

## Urutan penting

`NEXT_PUBLIC_API_BASE_URL` **dibakar saat build**, bukan dibaca saat runtime. URL API
harus sudah diketahui sebelum web di-build. Karena itu urutannya:

```
1. Deploy API          →  dapatkan URL API
2. Deploy web          →  pakai URL API sebagai build-time env
3. Update CORS di API  →  izinkan domain web
4. Uji end-to-end
```

Membalik langkah 1 dan 2 berarti web perlu di-build dua kali.

---

## Langkah 1 — Deploy API ke Railway

### 1.1 Buat service

1. Buka [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Pilih repository `smart-living-API`
3. Railway akan membuat satu service

### 1.2 Arahkan ke Dockerfile

Buka **Settings** service, atur:

| Setting | Nilai | Alasan |
|---|---|---|
| Root Directory | `/` (root repo) | Image butuh `data/recipes/` yang ada di luar `apps/api/` |
| Builder | `Dockerfile` | |
| Dockerfile Path | `docker/api.Dockerfile` | |

> **Jangan** set Root Directory ke `apps/api`. Build context harus root repo, kalau tidak
> `COPY data/recipes` gagal.

### 1.3 Set environment variable

Buka tab **Variables**:

| Variabel | Nilai awal | Keterangan |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:3000` | Diperbarui di langkah 3 |
| `LOG_LEVEL` | `INFO` | |

Yang **tidak perlu** diset — sudah ada default di `docker/api.Dockerfile` atau
`app/core/config.py`:

- `PORT` — disuntikkan Railway otomatis, dan `CMD` sudah membacanya
- `RECIPES_PATH`, `INGREDIENTS_PATH` — sudah absolut di Dockerfile
- `DEFAULT_LIMIT`, `MAX_LIMIT`, `MIN_MATCH_THRESHOLD` — default sudah sesuai kontrak

### 1.4 Aktifkan domain publik

**Settings → Networking → Generate Domain**. Catat URL-nya, misalnya:

```
https://smart-living-api-production.up.railway.app
```

### 1.5 Verifikasi

```bash
curl https://<URL_API_RAILWAY>/api/v1/health
```

Harus mengembalikan:

```json
{"status":"ok","recipeCount":60,"ingredientCount":94}
```

`recipeCount: 60` membuktikan dataset benar-benar ter-load di dalam image — bukan hanya
"API merespons".

---

## Langkah 2 — Deploy web ke Vercel

### 2.1 Import project

1. Buka [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import repository `smart-living-API`

### 2.2 Konfigurasi

| Setting | Nilai |
|---|---|
| Framework Preset | Next.js |
| Root Directory | `apps/web` |
| Build Command | `pnpm build` (default) |
| Install Command | `pnpm install --frozen-lockfile` |

Vercel membaca `packageManager` di `package.json` dan memakai pnpm 11.24.0 otomatis.

### 2.3 Environment variable

**Environment Variables**, untuk semua environment (Production, Preview, Development):

| Variabel | Nilai |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | URL API dari langkah 1.4, **tanpa trailing slash** |

Contoh: `https://smart-living-api-production.up.railway.app`

### 2.4 Deploy & catat domain

Setelah deploy sukses, catat domain-nya, misalnya:

```
https://smart-living-api-web.vercel.app
```

Pada tahap ini web sudah hidup tapi **request ke API akan gagal karena CORS** — itu
diperbaiki di langkah berikutnya.

---

## Langkah 3 — Update CORS di Railway

Kembali ke Railway → service API → **Variables**:

```
CORS_ORIGINS = https://smart-living-api-web.vercel.app
```

Railway akan redeploy otomatis.

### Bila ingin mengizinkan preview deployment Vercel

Vercel membuat domain unik per pull request. Untuk mengizinkannya, tambahkan domain yang
diperlukan dipisah koma:

```
CORS_ORIGINS = https://smart-living-api-web.vercel.app,https://smart-living-api-web-git-dev.vercel.app
```

`CORS_ORIGINS` menerima format comma-separated maupun JSON array.

> **Jangan pakai `*`.** Konfigurasi CORS yang terbuka membuat API bisa dipanggil dari
> situs mana pun. Aturan ini juga tercatat sebagai larangan eksplisit di
> `docs/technical-architecture.md` §17.

---

## Langkah 4 — Verifikasi production

### 4.1 API

```bash
# Health + dataset
curl https://<URL_API>/api/v1/health

# Rekomendasi
curl -X POST https://<URL_API>/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["telur","ayam","wortel"]}'

# CORS preflight dari domain web
curl -i -X OPTIONS https://<URL_API>/api/v1/recommendations \
  -H "Origin: https://<DOMAIN_WEB>" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Preflight harus mengembalikan `access-control-allow-origin` yang berisi domain web.

### 4.2 Web

Buka domain Vercel dan lalui alur:

1. Masukkan `telur, ayam, wortel` → kartu resep muncul
2. Chip normalisasi menampilkan `telur → Telur`
3. Masukkan `telur, kangkung` → chip "tidak dikenali" muncul, hasil tetap ada
4. Klik "Lihat Resep" → halaman detail terbuka
5. Klik "Kembali ke hasil" → balik ke halaman utama
6. Scroll ke bawah → section "Di balik layar" tampil, link OpenAPI berfungsi

### 4.3 Checklist keamanan

Periksa sebelum membagikan link demo:

- [ ] HTTPS aktif di kedua domain (Railway dan Vercel menyediakannya otomatis)
- [ ] `CORS_ORIGINS` berisi domain web saja — **bukan** `*`
- [ ] Tidak ada `.env` ter-commit: `git ls-files | grep -E "^\.env$|\.env\.local$"` harus kosong
- [ ] Bundle client tidak memuat secret — hanya variabel `NEXT_PUBLIC_*` yang sampai ke browser
- [ ] Response error tidak memuat stack trace: picu `curl -X POST <API>/api/v1/recommendations -d '{}' -H "Content-Type: application/json"` dan pastikan hanya ada `{"error": {...}}`
- [ ] Header `X-Request-ID` ada di response — untuk korelasi log

---

## Langkah 5 — Update README

Ganti baris demo di `README.md`:

```markdown
| **Demo** | https://<DOMAIN_WEB> |
| **API Docs** | https://<URL_API>/docs |
```

---

## Troubleshooting

### API: build gagal di Railway

Cek Root Directory. Harus `/`, bukan `apps/api` — `docker/api.Dockerfile` melakukan
`COPY data/recipes` yang hanya tersedia bila context-nya root repo.

### API: container start lalu mati

Lihat deploy log. Penyebab yang pernah terjadi: dataset tidak ditemukan. Verifikasi
`RECIPES_PATH` dan `INGREDIENTS_PATH` — di image keduanya sudah diset absolut ke
`/app/data/recipes/`, jadi jangan di-override kecuali memang perlu.

### Web: request ke API gagal dengan CORS error

Tiga hal yang perlu dicek:

1. `CORS_ORIGINS` di Railway sudah berisi domain Vercel (persis, termasuk `https://`)
2. Tidak ada trailing slash di `NEXT_PUBLIC_API_BASE_URL`
3. Railway sudah selesai redeploy setelah variabel diubah

### Web: memanggil `localhost:8000` di production

`NEXT_PUBLIC_API_BASE_URL` belum diset saat build, atau diset setelah build berjalan.
Variabel ini dibakar ke bundle — **redeploy** diperlukan setelah mengubahnya, bukan
sekadar restart.

### Web: build gagal dengan `ERR_PNPM_IGNORED_BUILDS`

`apps/web/pnpm-workspace.yaml` tidak terbaca. File itu menyimpan setting `allowBuilds`
dan harus ada di Root Directory yang dikonfigurasi (`apps/web`).

---

## Menjalankan container secara lokal

Untuk menguji image yang sama dengan production tanpa deploy:

```bash
docker compose up --build
# API: http://localhost:8000
# Web: http://localhost:3000
```

<details>
<summary>Docker di macOS tanpa Docker Desktop</summary>

Docker Desktop berat di mesin dengan RAM terbatas. Alternatifnya
[Colima](https://colima.run):

```bash
brew install colima docker docker-compose
colima start --cpu 2 --memory 2 --disk 20
docker compose up --build
```

`colima stop` membebaskan resource saat tidak dipakai.

</details>

Build image juga diverifikasi otomatis di CI (job `docker`): kedua image dibangun,
dijalankan, lalu di-smoke test. Kalau Dockerfile rusak, CI merah sebelum sampai
production.

---

## Dokumen terkait

| Dokumen | Isi |
|---|---|
| [`../README.md`](../README.md) | Cara menjalankan lokal, contoh API |
| [`technical-architecture.md`](technical-architecture.md) | §17 keamanan, §23 strategi Docker, §25 arsitektur deployment |
| [`../docker-compose.yml`](../docker-compose.yml) | Orkestrasi lokal |
| [`../docker/api.Dockerfile`](../docker/api.Dockerfile) | Image API — dipakai Railway |
| [`../docker/web.Dockerfile`](../docker/web.Dockerfile) | Image web — dipakai compose & CI |
