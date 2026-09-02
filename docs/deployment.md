# Panduan Deployment

Web ke **Vercel**, API ke **Hugging Face Spaces** lewat Dockerfile.

---

## Mengapa platform ini

Kebutuhannya sempit: satu container Python stateless, dataset 96 KB read-only, dan biaya
yang berkelanjutan untuk proyek portfolio.

| Platform | Docker | Biaya | Kartu kredit | Keputusan |
|---|---|---|---|---|
| **Hugging Face Spaces** | Ya | Gratis permanen | **Tidak perlu** | **Dipilih** |
| Railway | Ya | Trial $5 / 30 hari, lalu berbayar | Perlu | Trial berbatas waktu |
| Koyeb | Ya | Mulai $29/bulan | Perlu | Tidak ada free tier |
| Google Cloud Run | Ya | Gratis dalam kuota | Perlu | Butuh kartu kredit |
| Fly.io | Ya | ~$0,05/bulan dengan auto-stop | Perlu | Butuh kartu kredit |
| Render | Ya | Free tier | Tidak perlu | Cold start ~50 detik |
| Cloudflare Workers | **Tidak** | Gratis | Tidak perlu | Pyodide/WASM, bukan container |

Hugging Face Spaces adalah satu-satunya yang memenuhi tiga syarat sekaligus: mendukung
Docker, gratis permanen (bukan trial), dan tidak meminta kartu kredit.

Konsekuensi yang diterima: Space gratis tidur setelah beberapa waktu tidak diakses, dan
URL-nya berbentuk `<user>-<space>.hf.space`. Untuk demo portfolio, kedua hal itu dapat
diterima.

Cloudflare Workers sengaja dilewati meski gratis: ia menjalankan Python di Pyodide/WASM,
bukan container. Memakainya berarti `docker/api.Dockerfile` tidak lagi dipakai di
production — kehilangan alasan utama proyek ini memakai Docker.

---

## Urutan penting

`NEXT_PUBLIC_API_BASE_URL` **dibakar saat build**, bukan dibaca saat runtime. URL API
harus sudah diketahui sebelum web di-build:

```
1. Deploy API          →  dapatkan URL API
2. Deploy web          →  pakai URL API sebagai build-time env
3. Update CORS di API  →  izinkan domain web
4. Uji end-to-end
```

Membalik langkah 1 dan 2 berarti web perlu di-build dua kali.

---

## Langkah 1 — Deploy API ke Hugging Face Spaces

### 1.1 Cara sinkronisasi

HF Spaces punya dua batasan yang memengaruhi struktur:

- Hanya membaca `Dockerfile` di root repo Space — tidak ada opsi path seperti platform lain.
- Konfigurasi Space berada di YAML front matter `README.md`.

Keduanya bertabrakan dengan repo ini: Dockerfile berada di `docker/api.Dockerfile`
(karena build context-nya root repo, agar `data/recipes/` bisa di-`COPY`), dan `README.md`
sudah dipakai sebagai dokumentasi portfolio.

Solusinya: workflow `.github/workflows/deploy-hf.yml` menyiapkan *staging directory* yang
**meniru struktur repo**, lalu mem-push-nya ke Space.

```
staging/
├── Dockerfile            ← salinan docker/api.Dockerfile, TIDAK diubah
├── README.md             ← dari docker/hf-space-README.md (front matter YAML)
├── apps/api/
│   ├── app/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .python-version
└── data/recipes/
```

Karena path di dalam staging identik dengan yang dirujuk Dockerfile, image yang dibangun
HF **sama persis** dengan yang diverifikasi CI lewat `docker compose`. Tidak ada Dockerfile
versi kedua yang bisa menyimpang.

Sinkronisasi berjalan otomatis setiap kali workflow `CI` sukses di branch `main`. Kode
yang gagal test tidak akan pernah sampai ke production.

### 1.2 Buat Space

1. Buka [huggingface.co/new-space](https://huggingface.co/new-space)
2. **Space name**: `smart-living-api`
3. **SDK**: pilih **Docker** → template **Blank**
4. **Visibility**: Public
5. **Create Space**

Space akan kosong — itu normal, isinya datang dari CI.

### 1.3 Siapkan token

1. HF → **Settings** → **Access Tokens** → **New token**
2. Nama bebas (mis. `github-actions`), **Role: Write**
3. Copy token

Lalu di GitHub:

1. Repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**: nama `HF_TOKEN`, isi token tadi

Tanpa secret ini workflow akan gagal dengan pesan yang jelas, bukan error yang
membingungkan.

### 1.4 Trigger deploy pertama

Dua cara:

- **Otomatis**: push apa pun ke `main`. Setelah CI hijau, `deploy-hf` berjalan sendiri.
- **Manual**: GitHub → tab **Actions** → **Deploy API to Hugging Face Spaces** → **Run workflow**.

### 1.5 Pantau build

Buka halaman Space → tab **Logs**.

| Tab | Yang dicari |
|---|---|
| **Build** | `Pushing Image`, lalu `Scheduling Space` |
| **Container** | `Uvicorn running on http://0.0.0.0:8000` |

Build pertama memakan 2–4 menit (multi-stage + `uv sync`). Build berikutnya lebih cepat
karena layer dependency ter-cache.

### 1.6 Set variable

Space → **Settings** → **Variables and secrets** → **New variable**:

| Variabel | Nilai awal |
|---|---|
| `CORS_ORIGINS` | `http://localhost:3000` |

Diperbarui di langkah 3 setelah domain Vercel diketahui.

Yang **tidak perlu** diset — sudah ada default di Dockerfile atau `app/core/config.py`:
`RECIPES_PATH`, `INGREDIENTS_PATH`, `DEFAULT_LIMIT`, `MAX_LIMIT`, `MIN_MATCH_THRESHOLD`.

### 1.7 Verifikasi

```bash
curl https://callmerev95-smart-living-api.hf.space/api/v1/health
```

Harus mengembalikan:

```json
{"status":"ok","recipeCount":60,"ingredientCount":94}
```

Angka `60` yang penting — ia membuktikan dataset benar-benar ada di dalam image, bukan
hanya bahwa API merespons.

Dokumentasi interaktif: `https://callmerev95-smart-living-api.hf.space/docs`

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

**Sebelum** klik Deploy, tambahkan untuk semua environment (Production, Preview,
Development):

| Variabel | Nilai |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://callmerev95-smart-living-api.hf.space` |

Tanpa trailing slash. Kalau variabel ini ditambahkan setelah deploy pertama, aplikasi akan
build sukses tapi gagal saat dipakai — nilainya dibakar ke bundle, jadi butuh **redeploy**,
bukan restart.

### 2.4 Deploy & catat domain

Setelah deploy sukses, catat domainnya, misalnya:

```
https://smart-living-api.vercel.app
```

Pada tahap ini web sudah hidup tapi request ke API masih gagal karena CORS — diperbaiki di
langkah berikutnya.

---

## Langkah 3 — Update CORS di Space

Space → **Settings** → **Variables and secrets** → ubah `CORS_ORIGINS`:

```
CORS_ORIGINS = https://smart-living-api.vercel.app
```

Space akan restart otomatis (~30 detik).

### Mengizinkan preview deployment Vercel

Vercel membuat domain unik per pull request. Tambahkan domain yang diperlukan, dipisah
koma:

```
CORS_ORIGINS = https://smart-living-api.vercel.app,https://smart-living-api-git-dev.vercel.app
```

`CORS_ORIGINS` menerima format comma-separated maupun JSON array.

> **Jangan pakai `*`.** Konfigurasi CORS terbuka membuat API bisa dipanggil dari situs mana
> pun. Aturan ini tercatat sebagai larangan eksplisit di
> `docs/technical-architecture.md` §17.

---

## Langkah 4 — Verifikasi production

### 4.1 API

```bash
API=https://callmerev95-smart-living-api.hf.space
WEB=https://smart-living-api.vercel.app

# Health + dataset
curl -fsS "$API/api/v1/health"

# Rekomendasi
curl -fsS -X POST "$API/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["telur","ayam","wortel"]}'

# CORS preflight dari domain web
curl -i -X OPTIONS "$API/api/v1/recommendations" \
  -H "Origin: $WEB" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Preflight harus mengembalikan header `access-control-allow-origin` berisi domain web.

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

- [ ] HTTPS aktif di kedua domain (HF dan Vercel menyediakannya otomatis)
- [ ] `CORS_ORIGINS` berisi domain web saja — **bukan** `*`
- [ ] Tidak ada `.env` ter-commit: `git ls-files | grep -E "^\.env$|\.env\.local$"` harus kosong
- [ ] Bundle client tidak memuat secret — hanya variabel `NEXT_PUBLIC_*` yang sampai ke browser
- [ ] Response error tidak memuat stack trace:
      `curl -X POST "$API/api/v1/recommendations" -H "Content-Type: application/json" -d '{}'`
      harus hanya berisi `{"error": {...}}`
- [ ] Header `X-Request-ID` ada di response — untuk korelasi log

---

## Langkah 5 — Update README

Ganti baris demo di `README.md`:

```markdown
| **Demo** | https://smart-living-api.vercel.app |
| **API Docs** | https://callmerev95-smart-living-api.hf.space/docs |
```

---

## Keterbatasan Space gratis

**Space tidur setelah beberapa waktu tidak diakses.** Request pertama setelah bangun
memerlukan beberapa detik, dan berpotensi mengembalikan halaman loading HTML alih-alih
JSON.

Penanganan error yang sudah ada menurunkan dampaknya: bila response bukan JSON,
`lib/api/client.ts` melempar `UNKNOWN_ERROR` dan UI menampilkan pesan beserta tombol
"Coba lagi". Klik retry setelah Space bangun akan berhasil — tidak ada crash.

Bila di kemudian hari ini terasa mengganggu, ada tiga opsi:

| Opsi | Konsekuensi |
|---|---|
| Terima sebagai keterbatasan | Nol perubahan kode; reviewer mungkin perlu refresh sekali |
| Retry otomatis di API client | Demo mulus, tapi menambah kode yang hanya melayani demo |
| Cron ping `/api/v1/health` | Space tetap bangun, tapi mengakali batasan platform dan memakai kuota Actions |

---

## Troubleshooting

### Workflow gagal: `Secret HF_TOKEN belum diset`

Buat token dengan role **Write** di HF Settings → Access Tokens, lalu tambahkan sebagai
repository secret bernama `HF_TOKEN` di GitHub.

### Workflow gagal saat push: `Authentication failed`

Token kedaluwarsa atau role-nya **Read** alih-alih **Write**. Buat token baru dan perbarui
secret.

### HF build gagal: `COPY failed: no source files`

Struktur staging tidak cocok dengan yang dirujuk Dockerfile. Workflow punya step
"Verifikasi isi staging" yang seharusnya menangkap ini lebih dulu — periksa log step
tersebut.

### Space status `Runtime error`, container mati

Buka tab **Container** di Logs. Penyebab yang mungkin: dataset tidak ditemukan. Verifikasi
`RECIPES_PATH` dan `INGREDIENTS_PATH` — keduanya sudah diset absolut di Dockerfile
(`/app/data/recipes/`), jadi jangan di-override kecuali memang perlu.

### Space menampilkan halaman HTML, bukan JSON

Space sedang bangun dari tidur. Tunggu beberapa detik dan coba lagi.

### Web: CORS error di browser

Tiga hal yang perlu dicek:

1. `CORS_ORIGINS` di Space sudah berisi domain Vercel — persis, termasuk `https://`
2. Tidak ada trailing slash di `NEXT_PUBLIC_API_BASE_URL`
3. Space sudah selesai restart setelah variabel diubah

### Web: memanggil `localhost:8000` di production

`NEXT_PUBLIC_API_BASE_URL` belum diset saat build, atau diset setelah build berjalan.
Variabel ini dibakar ke bundle — lakukan **redeploy**, bukan sekadar restart.

### Web: build gagal dengan `ERR_PNPM_IGNORED_BUILDS`

`apps/web/pnpm-workspace.yaml` tidak terbaca. File itu menyimpan setting `allowBuilds` dan
harus ada di Root Directory yang dikonfigurasi (`apps/web`).

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
production — dan `deploy-hf` tidak akan berjalan karena ia menunggu CI sukses.

---

## Dokumen terkait

| Dokumen | Isi |
|---|---|
| [`../README.md`](../README.md) | Cara menjalankan lokal, contoh API |
| [`technical-architecture.md`](technical-architecture.md) | §17 keamanan, §23 strategi Docker, §25 arsitektur deployment |
| [`../docker-compose.yml`](../docker-compose.yml) | Orkestrasi lokal |
| [`../docker/api.Dockerfile`](../docker/api.Dockerfile) | Image API — dipakai HF Spaces |
| [`../docker/web.Dockerfile`](../docker/web.Dockerfile) | Image web — dipakai compose & CI |
| [`../docker/hf-space-README.md`](../docker/hf-space-README.md) | README + front matter untuk Space |
| [`../.github/workflows/deploy-hf.yml`](../.github/workflows/deploy-hf.yml) | Workflow sinkronisasi |
