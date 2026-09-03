# Panduan Deployment

Web **dan** API di **Vercel**. Web sebagai aplikasi Next.js, API sebagai Python Function.

---

## Mengapa Vercel untuk keduanya

Kebutuhannya sempit: satu aplikasi Python stateless, dataset 96 KB read-only, dan biaya
yang berkelanjutan untuk proyek portfolio — tanpa kartu kredit.

| Platform | Docker di production | Biaya | Kartu kredit | Keputusan |
|---|---|---|---|---|
| **Vercel Python Functions** | Tidak | Gratis permanen | **Tidak perlu** | **Dipilih** |
| Hugging Face Spaces | Ya | Docker SDK butuh PRO $9/bln | Tidak perlu | Docker Spaces berbayar |
| Railway | Ya | Trial $5 / 30 hari | Perlu | Trial berbatas waktu |
| Koyeb | Ya | Mulai $29/bulan | Perlu | Tidak ada free tier |
| Google Cloud Run | Ya | Gratis dalam kuota | Perlu | Butuh kartu kredit |
| Fly.io | Ya | ~$0,05/bulan | Perlu | Butuh kartu kredit |
| Render | Ya | Free tier | Tidak perlu | Cold start ~50 detik |
| Cloudflare Workers | Tidak | Gratis | Tidak perlu | Pyodide/WASM, kompleksitas konversi |

Setelah Docker Spaces di Hugging Face berpindah ke plan PRO, tidak ada lagi platform yang
memenuhi ketiga syarat sekaligus (Docker di production, gratis permanen, tanpa kartu
kredit). Trade-off harus dipilih.

Vercel dipilih karena mengorbankan hal yang paling sedikit merugikan: Docker tidak dipakai
di jalur production, tetapi tetap dipakai untuk pengembangan lokal (`docker compose`) dan
**diverifikasi otomatis di CI** — job `docker` membangun kedua image, menjalankannya, lalu
melakukan smoke test pada setiap push. Jadi kemampuan containerization tetap terbukti,
bukan sekadar diklaim.

Sebagai imbalannya: satu platform untuk web dan API (satu dashboard, satu tempat
environment variable), cold start 1–2 detik alih-alih 50 detik seperti Render, dan tidak
ada batas waktu trial.

Konsekuensi yang diterima: request pertama setelah function idle memerlukan 1–2 detik.

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

Karena keduanya di Vercel, ini menjadi **dua project terpisah** dari repository yang sama,
dibedakan oleh Root Directory.

---

## Langkah 1 — Deploy API ke Vercel

### 1.1 Cara kerjanya

Vercel Python Runtime memuat `index.py` di root project dan mencari variabel top-level
bernama `app`. Tiga berkas di root repo yang mengaturnya:

| Berkas | Peran |
|---|---|
| `index.py` | Entrypoint — mengatur `sys.path` lalu re-export `app`, tanpa logika |
| `requirements.txt` | Dependency runtime: fastapi, pydantic, pydantic-settings |
| `vercel.json` | `excludeFiles` agar bundle ramping (web, test, docs tidak ikut) |

`uvicorn` sengaja **tidak** ada di `requirements.txt` — Vercel memuat ASGI app secara
langsung, servernya disediakan platform. Menyertakannya hanya memperbesar bundle.

#### Kenapa entrypoint mengatur `sys.path`

Seluruh modul di `apps/api/app/` memakai import absolut `from app.xxx import ...` — ada 61
tempat. Konvensi itu bekerja karena `apps/api` selalu berada di `sys.path`:

| Lingkungan | Mekanisme |
|---|---|
| pytest | `pythonpath = ["."]` di `pyproject.toml`, dijalankan dari `apps/api` |
| Docker | `WORKDIR /app` dengan `app/` sebagai subfolder langsung |
| Vercel | **Hanya root repo di `sys.path`** — entrypoint harus menambahkannya sendiri |

Tanpa penyesuaian itu, function gagal dengan `FUNCTION_INVOCATION_FAILED` yang di log
muncul sebagai `ModuleNotFoundError: No module named 'app'`. Yang menipu: build tetap
sukses, karena `index.py` sendiri valid — error baru muncul saat modul yang diimpornya
dieksekusi.

Menyesuaikan `sys.path` di satu berkas dipilih ketimbang mengubah 61 import menjadi
relatif: konvensi absolut sudah terbukti di pytest dan Docker, dan mengubahnya berisiko
merusak dua jalur yang berjalan baik.

#### Dataset

Dataset di `data/recipes/` ikut ter-deploy karena tidak dikecualikan. `Settings`
menemukannya lewat `_find_repo_root()` yang menelusuri ancestor sampai menemukan folder
`data/recipes` — layout Vercel identik dengan checkout, jadi tidak ada perubahan kode.

Konsistensi ketiga berkas dijaga oleh `apps/api/tests/unit/test_vercel_deployment.py`:
versi di `requirements.txt` harus sama dengan `pyproject.toml`, `uvicorn` tidak boleh ada,
dataset tidak boleh masuk `excludeFiles`, entrypoint harus mengatur `sys.path`, dan
entrypoint tidak boleh berisi logika.

### 1.2 Buat project

1. Buka [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import repository `smart-living-API`
3. **Project Name**: `smart-living-api` (menentukan subdomain)

### 1.3 Konfigurasi

| Setting | Nilai | Catatan |
|---|---|---|
| Framework Preset | **Other** | Vercel mendeteksi Python dari `requirements.txt` |
| Root Directory | `/` | **Root repo**, bukan `apps/api` — dataset ada di luar folder itu |
| Build Command | *(kosongkan)* | Tidak ada langkah build untuk Python |
| Output Directory | *(kosongkan)* | |
| Install Command | *(biarkan default)* | |

Root Directory `/` adalah titik yang paling sering salah. `index.py` mengimpor
`apps.api.app.main`, dan dataset berada di `data/recipes/` — keduanya hanya terjangkau
bila context-nya root repo.

### 1.4 Environment variable

Sebelum deploy, tambahkan untuk semua environment:

| Variabel | Nilai awal |
|---|---|
| `CORS_ORIGINS` | `http://localhost:3000` |
| `LOG_LEVEL` | `INFO` |

`CORS_ORIGINS` diperbarui di langkah 3 setelah domain web diketahui.

Yang **tidak perlu** diset — default di `app/core/config.py` sudah sesuai:
`RECIPES_PATH`, `INGREDIENTS_PATH`, `DEFAULT_LIMIT`, `MAX_LIMIT`,
`MIN_MATCH_THRESHOLD`, `MAX_INGREDIENTS_PER_REQUEST`, `MAX_INGREDIENT_NAME_LENGTH`.

### 1.5 Deploy & verifikasi

Klik **Deploy**, tunggu 1–2 menit, catat URL yang dihasilkan (mis.
`https://smart-living-api.vercel.app`).

```bash
API=https://smart-living-api.vercel.app

curl -fsS "$API/api/v1/health"
```

Harus mengembalikan:

```json
{"status":"ok","recipeCount":60,"ingredientCount":94}
```

Angka `60` yang penting — ia membuktikan dataset benar-benar ikut ter-deploy, bukan hanya
bahwa function merespons.

Dokumentasi interaktif: `https://smart-living-api.vercel.app/docs`

---

## Langkah 2 — Deploy web ke Vercel

Project **kedua** dari repository yang sama.

### 2.1 Import

1. Vercel → **Add New** → **Project** → import `smart-living-API` lagi
2. **Project Name**: `smart-living-web` (atau nama lain — harus berbeda dari project API)

### 2.2 Konfigurasi

| Setting | Nilai |
|---|---|
| Framework Preset | Next.js |
| Root Directory | `apps/web` |
| Build Command | `pnpm build` (default) |
| Install Command | `pnpm install --frozen-lockfile` |

Vercel membaca `packageManager` di `package.json` dan memakai pnpm 11.24.0 otomatis.

### 2.3 Environment variable

**Sebelum** klik Deploy:

| Variabel | Nilai |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | URL API dari langkah 1.5, **tanpa trailing slash** |

Kalau variabel ini ditambahkan setelah deploy pertama, aplikasi akan build sukses tapi
gagal saat dipakai — nilainya dibakar ke bundle, jadi butuh **redeploy**, bukan restart.

### 2.4 Deploy & catat domain

Setelah sukses, catat domainnya (mis. `https://smart-living-web.vercel.app`).

Pada tahap ini web sudah hidup tapi request ke API masih gagal karena CORS — diperbaiki di
langkah berikutnya.

---

## Langkah 3 — Update CORS di project API

Vercel → project **API** → **Settings** → **Environment Variables** → edit `CORS_ORIGINS`:

```
CORS_ORIGINS = https://smart-living-web.vercel.app
```

Lalu **Deployments** → deployment terakhir → **Redeploy**. Perubahan environment variable
tidak otomatis memicu redeploy.

### Mengizinkan preview deployment

Vercel membuat domain unik per pull request. Tambahkan domain yang diperlukan, dipisah
koma:

```
CORS_ORIGINS = https://smart-living-web.vercel.app,https://smart-living-web-git-dev-callmerev95.vercel.app
```

`CORS_ORIGINS` menerima format comma-separated maupun JSON array.

> **Jangan pakai `*`.** Konfigurasi CORS terbuka membuat API bisa dipanggil dari situs mana
> pun. Aturan ini tercatat sebagai larangan eksplisit di
> `docs/technical-architecture.md` §17.

---

## Langkah 4 — Verifikasi production

### 4.1 API

```bash
API=https://smart-living-api.vercel.app
WEB=https://smart-living-web.vercel.app

# Health + dataset
curl -fsS "$API/api/v1/health"

# Rekomendasi
curl -fsS -X POST "$API/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["telur","ayam","wortel"]}'

# Bahan tak dikenal — harus 200, bukan error
curl -fsS -X POST "$API/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["telur","kangkung"]}'

# Detail resep
curl -fsS "$API/api/v1/recipes/recipe_001"

# 404 yang benar
curl -s -o /dev/null -w '%{http_code}\n' "$API/api/v1/recipes/recipe_999"

# CORS preflight dari domain web
curl -i -X OPTIONS "$API/api/v1/recommendations" \
  -H "Origin: $WEB" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Preflight harus mengembalikan header `access-control-allow-origin` berisi domain web.

### 4.2 Web

Buka domain web dan lalui alur:

1. Masukkan `telur, ayam, wortel` → kartu resep muncul
2. Chip normalisasi menampilkan `telur → Telur`
3. Masukkan `telur, kangkung` → chip "tidak dikenali" muncul, hasil tetap ada
4. Klik "Lihat Resep" → halaman detail terbuka
5. Klik "Kembali ke hasil" → balik ke halaman utama
6. Scroll ke bawah → section "Di balik layar" tampil, link OpenAPI berfungsi

### 4.3 Checklist keamanan

Periksa sebelum membagikan link demo:

- [ ] HTTPS aktif di kedua domain (Vercel menyediakannya otomatis)
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
| **Demo** | https://smart-living-web.vercel.app |
| **API Docs** | https://smart-living-api.vercel.app/docs |
```

---

## Karakteristik serverless

**Cold start 1–2 detik.** Function yang idle akan "tidur"; request pertama setelahnya
memerlukan waktu untuk inisialisasi. Sesudah itu request berjalan normal.

Yang mempengaruhi cold start di proyek ini: dataset 96 KB dimuat sekali saat inisialisasi
modul lewat composition root yang di-`lru_cache`. Karena kecil, dampaknya minimal.

**Filesystem read-only.** API ini murni membaca — tidak ada operasi tulis ke disk sama
sekali (diverifikasi: tidak ada `write_text`, `mkdir`, atau `tempfile` di `app/`). Jadi
batasan ini tidak berpengaruh.

**Tanpa state antar request.** Recommendation engine deterministik dan stateless, jadi
tidak ada yang perlu dipertahankan antar invocation.

---

## Troubleshooting

### `FUNCTION_INVOCATION_FAILED` saat request, padahal build sukses

Runtime Logs akan menampilkan `ModuleNotFoundError: No module named 'app'`.

Penyebab: `index.py` tidak menambahkan `apps/api` ke `sys.path`, sehingga import absolut
`from app.xxx` gagal ketika `main.py` dieksekusi (lihat §1.1). Yang menipu: build tetap
sukses karena `index.py` sendiri valid.

Test `test_entrypoint_adds_apps_api_to_sys_path` menjaga ini agar tidak terulang.

### Build gagal: `ModuleNotFoundError` untuk modul lain

Root Directory bukan `/`. Entrypoint dan `data/recipes/` hanya terjangkau bila context-nya
root repo.

### Function error: dataset tidak ditemukan

Dua kemungkinan:

1. `data/` masuk ke `excludeFiles` di `vercel.json` — periksa, seharusnya tidak ada. Test
   `test_dataset_not_excluded` menjaga ini.
2. Root Directory salah, sehingga `data/recipes/` tidak ikut ter-deploy.

### Bundle melewati batas ukuran

Periksa `excludeFiles` di `vercel.json`. Yang seharusnya dikecualikan: `apps/web/**`,
`apps/api/tests/**`, `apps/api/scripts/**`, `apps/api/.venv/**`, `docs/**`, `docker/**`,
`.github/**`, dan artefak `__pycache__`.

### Response 404 untuk semua endpoint

Vercel tidak menemukan entrypoint. Pastikan `index.py` ada di root repo dan mengekspor
variabel bernama `app` (bukan `handler` atau nama lain).

### Web: CORS error di browser

Tiga hal yang perlu dicek:

1. `CORS_ORIGINS` di project API sudah berisi domain web — persis, termasuk `https://`
2. Tidak ada trailing slash di `NEXT_PUBLIC_API_BASE_URL`
3. Project API sudah **di-redeploy** setelah variabel diubah

### Web: memanggil `localhost:8000` di production

`NEXT_PUBLIC_API_BASE_URL` belum diset saat build, atau diset setelah build berjalan.
Variabel ini dibakar ke bundle — lakukan **redeploy**, bukan sekadar restart.

### Web: build gagal dengan `ERR_PNPM_IGNORED_BUILDS`

`apps/web/pnpm-workspace.yaml` tidak terbaca. File itu menyimpan setting `allowBuilds` dan
harus ada di Root Directory yang dikonfigurasi (`apps/web`).

---

## Menjalankan container secara lokal

Docker tidak dipakai di jalur production, tetapi tetap dipelihara untuk pengembangan lokal
dan diverifikasi di CI:

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

Job `docker` di CI membangun kedua image, menjalankannya, lalu melakukan smoke test pada
health endpoint, halaman web, dan alur rekomendasi. Kalau Dockerfile rusak, CI merah.

---

## Dokumen terkait

| Dokumen | Isi |
|---|---|
| [`../README.md`](../README.md) | Cara menjalankan lokal, contoh API |
| [`technical-architecture.md`](technical-architecture.md) | §17 keamanan, §23 strategi Docker, §25 arsitektur deployment |
| [`../index.py`](../index.py) | Entrypoint Vercel Python Runtime |
| [`../requirements.txt`](../requirements.txt) | Dependency runtime untuk Vercel |
| [`../vercel.json`](../vercel.json) | Konfigurasi bundle function |
| [`../docker-compose.yml`](../docker-compose.yml) | Orkestrasi lokal |
| [`../docker/api.Dockerfile`](../docker/api.Dockerfile) | Image API — lokal & CI |
| [`../docker/web.Dockerfile`](../docker/web.Dockerfile) | Image web — lokal & CI |
