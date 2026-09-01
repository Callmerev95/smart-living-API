# Development Roadmap — Smart Living API

**Versi:** 1.0
**Status:** Draf Implementasi MVP
**Dokumen Terkait:** `prd.md`, `technical-architecture.md`, `component-architecture.md`, `content-schema.md`
**Tujuan Dokumen:** Menentukan urutan fase pengembangan, dependency antar fase, dan
exit criteria yang terukur — sehingga progres bisa dinilai objektif, bukan berdasarkan
perasaan "sudah hampir selesai".

---

## 0. Cara Membaca Dokumen Ini

Dokumen ini menjawab: **"dalam urutan apa MVP dibangun, dan kapan sebuah fase boleh
dianggap selesai?"**

**Sengaja tanpa estimasi waktu.** Ini proyek portfolio solo tanpa deadline eksternal.
Estimasi jam/hari akan jadi angka karangan yang menciptakan tekanan palsu. Yang dipakai
sebagai alat kontrol adalah **exit criteria** — kriteria biner yang bisa diverifikasi.

| Dokumen | Menjawab |
|---|---|
| `prd.md` | Apa & mengapa |
| `technical-architecture.md` | Bagaimana |
| `component-architecture.md` | Di mana & tanggung jawab siapa |
| `content-schema.md` | Data & kontrak |
| **`development-roadmap.md`** | **Dalam urutan apa & kapan selesai** |
| `implementation-task-breakdown.md` | Task konkret per file |

---

## 1. Peta Fase

```text
┌──────────────────────────────────────────────────────────────┐
│                          MVP                                 │
│                                                              │
│  P1 Foundation                                               │
│       ↓                                                      │
│  P2 Data ──────────────┐                                     │
│       ↓                │                                     │
│  P3 Core Engine        │  (P2 & P3 saling menguatkan:         │
│       ↓                │   dataset diuji lewat engine)        │
│  P4 API ───────────────┘                                     │
│       ↓                                                      │
│  P5 Frontend                                                 │
│       ↓                                                      │
│  P6 Portfolio & Deploy                                       │
└──────────────────────────────────────────────────────────────┘
                          ↓
              ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
              P7 AI Enhancement (FUTURE)
              Tidak dikerjakan di MVP
              ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
```

Urutan ini mengikuti `technical-architecture.md` §30 dan
`component-architecture.md` §37.

### 1.1 Prinsip Urutan

1. **Bottom-up di backend.** Domain dulu, HTTP terakhir. Alasan: matching engine bisa
   diuji tanpa menjalankan server (technical-architecture §1 prinsip 6), jadi feedback
   loop-nya paling cepat.
2. **Backend selesai sebelum frontend mulai.** Frontend butuh kontrak API yang stabil.
   Membangun keduanya paralel di proyek solo menghasilkan contract drift
   (technical-architecture §28).
3. **Data sebelum engine.** Engine tanpa dataset tidak bisa diuji dengan kasus nyata.
4. **Portfolio layer terakhir.** README, diagram, dan screenshot butuh produk yang sudah
   jalan. Menulisnya lebih awal = menulis dua kali.

### 1.2 Aturan Antar Fase

- **Jangan mulai fase berikut sebelum exit criteria fase sekarang terpenuhi.** Ini satu-satunya
  mekanisme yang mencegah penumpukan pekerjaan setengah jadi.
- Exit criteria bersifat **biner** — terpenuhi atau tidak, bukan "sebagian".
- Boleh kembali ke fase sebelumnya untuk perbaikan (dataset hampir pasti perlu iterasi
  setelah P3), tapi jangan melompati fase.

---

## 2. Phase 1 — Foundation

**Goal:** Repository bisa dijalankan, di-lint, dan di-test — meskipun belum ada fitur.

### 2.1 Kenapa Fase Ini Dulu

Setup tooling setelah kode banyak = refactor menyakitkan. Ruff yang baru dipasang di
tengah proyek akan melaporkan ratusan pelanggaran sekaligus. Lebih murah memasang
pagar sebelum menanam.

### 2.2 Deliverable

| Area | Isi |
|---|---|
| Struktur | `apps/api/`, `apps/web/`, `data/recipes/`, `docs/`, `docker/`, `.github/workflows/` |
| Backend | `uv` project, FastAPI terinstall, `app/main.py` minimal, `ruff` config, `pytest` config |
| Frontend | Next.js + TypeScript + Tailwind via `pnpm`, eslint, `vitest` config |
| Config | `.env.example`, `core/config.py` (Pydantic Settings), CORS |
| Git | `.gitignore`, repo GitHub, commit awal |
| CI | GitHub Actions: lint + typecheck + test untuk kedua app |

### 2.3 Exit Criteria

- [ ] `uv run uvicorn app.main:app --reload` jalan, `GET /api/v1/health` balas `200`
- [ ] `pnpm dev` jalan, halaman kosong render tanpa error
- [ ] `ruff check .` clean
- [ ] `pytest` jalan (boleh 1 test trivial) dan hijau
- [ ] `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` semuanya lewat
- [ ] `.env.example` ada, `.env` masuk `.gitignore`
- [ ] CI hijau di GitHub Actions
- [ ] Tidak ada secret di source code

### 2.4 Non-Goal Fase Ini

Jangan bikin: business logic, dataset, komponen UI, Docker multi-stage yang rumit,
PostgreSQL, Redis.

### 2.5 Risiko

| Risiko | Mitigasi |
|---|---|
| Overengineering setup (Nx, Turborepo, monorepo tooling berat) | Dua app independen dengan package manager masing-masing sudah cukup. Tidak ada shared code Python↔TS yang butuh orchestrator. |
| Config tersebar di banyak tempat | Semua config lewat `core/config.py` (backend) dan `lib/constants/` (frontend) |

---

## 3. Phase 2 — Data

**Goal:** Dataset 60 resep + ~120 ingredient valid, ter-load lewat repository abstraction.

**Dependency masuk:** P1 selesai.

### 3.1 Kenapa Fase Ini Sebelum Engine

Engine yang diuji dengan 3 resep buatan akan lolos test tapi gagal di dunia nyata.
Dataset nyata mengungkap masalah yang tidak terlihat: alias bertabrakan, resep tanpa
overlap bahan, semua skor 0% atau 100%.

### 3.2 Deliverable

| Item | Isi |
|---|---|
| `data/recipes/ingredients.json` | ~120 ingredient kanonik + alias + kategori + flag staple |
| `data/recipes/recipes.json` | 60 resep original |
| Validator script | Cek semua aturan `content-schema.md` §A.2.4 & §A.3.7 |
| `domain/models/` | `Ingredient`, `Recipe` — dataclass murni, tanpa framework |
| `repositories/base.py` | Interface `RecipeRepository`, `IngredientRepository` |
| `repositories/json_recipe_repository.py` | Implementasi JSON, load saat startup |

### 3.3 Strategi Eksekusi

Dataset dibangun **bertahap**, tidak sekaligus (`content-schema.md` §A.8.4):

```text
Batch 1 (15 resep) → validate → commit
Batch 2 (15 resep) → validate → commit
Batch 3 (15 resep) → validate → commit
Batch 4 (15 resep) → validate → commit
```

Ingredient baru masuk `ingredients.json` **sebelum** dipakai di resep. Validator
dijalankan setiap batch — bukan sekali di akhir, karena memperbaiki 60 resep sekaligus
lebih mahal daripada memperbaiki 15.

### 3.4 Exit Criteria

- [ ] 60 resep di `recipes.json`, id `recipe_001`–`recipe_060`, semua unik
- [ ] ~120 ingredient di `ingredients.json`, `name` semua unik
- [ ] 5–8 ingredient dengan `staple: true`
- [ ] Validator lewat 100%: **setiap** `ingredients[].name` di resep ada di `ingredients.json`
- [ ] Tidak ada alias duplikat lintas ingredient
- [ ] Setiap resep punya ≥2 required non-staple (guard divide-by-zero)
- [ ] Setiap resep punya 3–10 steps
- [ ] Distribusi difficulty mendekati target (~60/30/10)
- [ ] `JsonRecipeRepository.get_all()` mengembalikan 60 `Recipe`, `get_by_id()` bekerja
- [ ] `domain/models/` tidak import `fastapi` maupun `pydantic`
- [ ] Unit test repository hijau (load, count, get_by_id, id tidak ada → `None`)
- [ ] `source: "original"` di semua resep

### 3.5 Risiko

| Risiko | Mitigasi |
|---|---|
| Dataset tidak punya overlap bahan → matching terasa mati | Sengaja pakai bahan umum berulang (`content-schema.md` §A.8.2). Diverifikasi di exit criteria P3. |
| Alias bertabrakan → normalisasi ambigu | Validator menolak alias duplikat sejak batch pertama |
| Resep dikarang tanpa masuk akal kuliner | `content-schema.md` §A.8.5. Baca ulang tiap batch: "apakah ini benar-benar bisa dimasak?" |
| Referential integrity rusak silent | Validator adalah gate — dataset tidak boleh commit kalau gagal |

---

## 4. Phase 3 — Core Engine

**Goal:** Recommendation logic lengkap, deterministik, ter-unit-test, tanpa satu pun
import framework.

**Dependency masuk:** P2 selesai (butuh dataset nyata untuk test).

### 4.1 Kenapa Ini Inti Proyek

Ini nilai produk sebenarnya (`component-architecture.md` §40 Decision 1). Semua
lapisan lain — HTTP, React, Docker — adalah pembungkus. Kalau fase ini benar, sisanya
mekanis. Kalau fase ini salah, tidak ada polish frontend yang bisa menutupinya.

### 4.2 Deliverable

Urutan pembuatan sesuai `component-architecture.md` §37:

| Urutan | Komponen | File |
|---|---|---|
| 1 | `MatchResult` model | `domain/models/match_result.py` |
| 2 | Ingredient normalizer | `services/ingredient_normalizer.py` |
| 3 | Scoring (pure function) | `domain/matching/scoring.py` |
| 4 | Matching engine | `domain/matching/engine.py` |
| 5 | Ranking | `domain/matching/ranking.py` |
| 6 | Recommendation service | `services/recommendation_service.py` |

### 4.3 Aturan Implementasi

- Scoring adalah **pure function** — input primitif, output integer, tanpa side effect.
- Engine menerima `(user_ingredients, recipes, ingredient_dict)` dan mengembalikan
  `list[MatchResult]`. Tidak load file, tidak baca config global.
- Staple exclusion (`content-schema.md` §A.5) diterapkan di **scoring/engine**, bukan
  di route dan bukan di repository.
- Urutan operasi service: **normalize → get recipes → score → filter threshold → rank → limit**.
  Filter sebelum limit (`content-schema.md` §A.6).

### 4.4 Exit Criteria

- [ ] Semua test case normalisasi `content-schema.md` §A.4.5 (14 kasus) hijau
- [ ] Semua test case scoring `content-schema.md` §A.5.5 (8 kasus) hijau — termasuk
      case 4 & 5 (staple exclusion) dan case 8 (divide-by-zero guard)
- [ ] Semua test case ranking `content-schema.md` §A.6.1 (7 kasus) hijau
- [ ] `unknownIngredients` terisi benar untuk input di luar kamus, tanpa exception
- [ ] Determinisme terverifikasi: input yang sama dijalankan 2x → output identik
      (termasuk urutan array)
- [ ] `grep -r "fastapi\|pydantic" app/domain/` kosong
- [ ] `grep -r "requests\|httpx\|openai" app/domain/` kosong
- [ ] Semua test bisa jalan **tanpa** menyalakan server
- [ ] Coverage `domain/` dan `services/` ≥ 90%
- [ ] Smoke test manual pada dataset nyata: input `telur, ayam, wortel` menghasilkan
      ≥3 resep dengan **sebaran skor berbeda** (bukan semua 100% atau semua 0%)
- [ ] `ruff check .` clean

### 4.5 Gate Kualitas Dataset

Exit criteria terakhir di §4.4 adalah **gate balik ke P2**. Kalau sebaran skor tidak
muncul, masalahnya di dataset (overlap kurang), bukan di engine. Perbaiki dataset,
jangan tuning formula untuk menutupi.

Uji minimal 5 kombinasi input berbeda dan catat hasilnya:

| Input uji | Ekspektasi |
|---|---|
| `telur, ayam, wortel` | ≥3 hasil, ada gradasi skor |
| `tahu, tempe, kecap` | ≥3 hasil |
| `nasi, telur, bawang putih` | ≥3 hasil |
| `telur` (satu bahan) | ada hasil, skor rendah–sedang |
| `kangkung, durian` (unknown) | `results: []`, `unknownIngredients` terisi, tanpa error |

### 4.6 Risiko

| Risiko | Mitigasi |
|---|---|
| Business logic bocor ke service/route | Grep check di exit criteria + review dependency matrix |
| Ranking terasa tidak relevan | Benchmark 5 input nyata (§4.5), review manual — bukan asumsi |
| Non-determinisme dari iterasi `set` | Jangan andalkan urutan `set`. Urutan output mengikuti urutan `ingredients[]` resep. Ada test khusus determinisme. |
| Formula di-tuning untuk menutupi dataset lemah | Gate §4.5: masalah sebaran skor = masalah dataset |

---

## 5. Phase 4 — API

**Goal:** REST API lengkap dengan validasi, error handling konsisten, dan OpenAPI docs.

**Dependency masuk:** P3 selesai.

### 5.1 Deliverable

| Item | File |
|---|---|
| Request/response schema | `schemas/recommendation.py`, `recipe.py`, `ingredient.py`, `error.py` |
| Route recommendations | `api/v1/routes/recommendations.py` |
| Route recipes | `api/v1/routes/recipes.py` |
| Route ingredients | `api/v1/routes/ingredients.py` |
| Route health | `api/v1/routes/health.py` |
| Router aggregator | `api/v1/router.py` |
| Error handling | `core/errors.py` + exception handler global |
| Logging | `core/logging.py` — request_id, method, path, status, duration_ms |
| Dependency injection | Wiring repository → service ke route |

### 5.2 Aturan Implementasi

- Route hanya: **request → validation → service call → response**. Tidak ada perhitungan
  match percentage di route (`component-architecture.md` §13, §35).
- Response pakai `camelCase` via `alias_generator`, internal Python tetap `snake_case`
  (`AGENTS.md` §5).
- Semua error keluar dalam format `content-schema.md` §A.10.5. Tidak ada stack trace
  ke client.
- Implementasi **Delta v1.1** (`content-schema.md` §A.9): `unknownIngredients[]`,
  `query.raw` + `query.ingredients` canonical.

### 5.3 Exit Criteria

- [ ] `POST /api/v1/recommendations` bekerja sesuai kontrak `content-schema.md` §A.10.1
- [ ] Response punya `query.raw`, `query.ingredients`, `unknownIngredients`, `results`, `meta`
- [ ] `GET /api/v1/recipes/{id}` → 200 untuk id valid, 404 `RECIPE_NOT_FOUND` untuk invalid
- [ ] `GET /api/v1/ingredients` mengembalikan ~120 ingredient
- [ ] `GET /api/v1/health` mengembalikan `status`, `recipeCount: 60`, `ingredientCount`
- [ ] Integration test lewat untuk skenario: valid input, array kosong, field hilang,
      limit invalid (0, 11, string), unknown ingredient, tidak ada resep cocok,
      >30 bahan, nama bahan >60 karakter
- [ ] Semua error mengikuti format `{"error":{"code","message","details"}}`
- [ ] Tidak ada stack trace di response (verifikasi dengan memicu exception sengaja)
- [ ] `/docs` (Swagger) render, semua endpoint punya contoh request/response
- [ ] CORS mengizinkan `http://localhost:3000` saja (bukan `*`)
- [ ] `grep -rn "load_json\|open(" app/api/` kosong — route tidak akses data langsung
- [ ] Log berisi `request_id`, `method`, `path`, `status_code`, `duration_ms`; tidak ada secret
- [ ] Benchmark lokal: p50 < 200ms, p95 < 500ms (PRD §14) — diukur, bukan diasumsikan
- [ ] `ruff check .` clean, `pytest` hijau

### 5.4 Risiko

| Risiko | Mitigasi |
|---|---|
| Route jadi tempat business logic | Grep check + integration test yang memverifikasi perilaku, bukan implementasi |
| Kontrak response beda dari `content-schema.md` | Integration test membandingkan struktur response dengan contoh di §A.10.1 |
| Mismatch `camelCase`/`snake_case` | Satu base schema class dengan `alias_generator`, dipakai semua response schema |
| Performa tidak diukur | Benchmark masuk exit criteria sebagai angka, bukan klaim |

---

## 6. Phase 5 — Frontend

**Goal:** Demo interaktif yang memakai API nyata, dengan empat state eksplisit.

**Dependency masuk:** P4 selesai — kontrak API stabil.

### 6.1 Deliverable

Urutan pembuatan sesuai `component-architecture.md` §37:

| Urutan | Item |
|---|---|
| 1 | UI primitives (`Button`, `Input`, `Badge`, `Card`, `Skeleton`, `Alert`) |
| 2 | Types dari kontrak API (`types/api.ts`) |
| 3 | Content constants (`lib/constants/content.ts` dari `content-schema.md` Bagian B) |
| 4 | API client (`lib/api/client.ts`, `recommendations.ts`, `recipes.ts`, `ingredients.ts`) |
| 5 | Hook `useRecommendations` |
| 6 | `IngredientInput` + `IngredientTag` (chip normalisasi — Delta 3) |
| 7 | `RecommendationList` + `RecommendationCard` + `MatchBadge` |
| 8 | State: `RecommendationSkeleton`, `RecommendationEmpty`, `RecommendationError` |
| 9 | `RecipeDetail` + sub-component + halaman `recipes/[id]` |
| 10 | `HeroSection`, `Footer`, komposisi `app/page.tsx` |

### 6.2 Aturan Implementasi

- Tidak ada business logic di component. Tidak ada perhitungan match percentage,
  tidak ada normalisasi (`AGENTS.md` §4).
- Semua request lewat `lib/api/` — component tidak menyusun URL sendiri
  (`component-architecture.md` §11).
- Semua copy dari `lib/constants/content.ts`, bukan string literal di JSX
  (`content-schema.md` §B.12).
- Error API dipetakan lewat `error.code`, bukan menampilkan `error.message` mentah
  (`content-schema.md` §B.8).
- State terpisah jadi component sendiri, bukan conditional bertumpuk
  (`component-architecture.md` §30).

### 6.3 Exit Criteria

- [ ] Input bahan bekerja: comma-separated, submit via tombol dan Enter
- [ ] Frontend memakai API **nyata**, bukan mock atau data hardcode
- [ ] Chip normalisasi menampilkan mapping `telur → Telur` (Delta 3)
- [ ] Bahan unknown ditampilkan sebagai chip "tidak dikenali" (Delta 2)
- [ ] Empat state tampil benar: initial, loading (skeleton), success, empty, error
- [ ] Varian empty khusus "semua bahan tidak dikenali" (`content-schema.md` §B.5.5)
- [ ] `RecommendationCard` menampilkan match%, available, missing, waktu, difficulty, porsi
- [ ] Tier warna badge sesuai `content-schema.md` §B.6.2
- [ ] Halaman detail resep bisa dibuka, 404 ditangani
- [ ] Validasi client-side: input kosong, >30 bahan, nama >60 karakter
- [ ] Semua copy dari `content.ts` — `grep` string Indonesia di `components/` bersih
- [ ] Aksesibilitas: label pada input, `aria-live` untuk hasil, fokus terlihat,
      seluruh alur bisa dioperasikan dengan keyboard, kontras memadai
- [ ] Component test: input render, submit, loading, success, empty, error
- [ ] `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` semuanya lewat
- [ ] Contoh input di `content-schema.md` §B.3 diverifikasi menghasilkan ≥3 resep pada
      dataset final

### 6.4 Risiko

| Risiko | Mitigasi |
|---|---|
| Component jadi god-component (`RecipePage.tsx` berisi semuanya) | `component-architecture.md` §34 anti-pattern. Satu component satu tanggung jawab. |
| Business logic pindah ke frontend | Review: apakah component menghitung sesuatu yang seharusnya dari API? |
| Copy tersebar sebagai string literal | Grep check di exit criteria |
| Aksesibilitas diabaikan | Masuk exit criteria, bukan nice-to-have |

---

## 7. Phase 6 — Portfolio & Deploy

**Goal:** Reviewer bisa memahami produk, arsitektur, dan trade-off tanpa membaca source
code — lalu mencobanya sendiri lewat URL live.

**Dependency masuk:** P5 selesai.

### 7.1 Kenapa Fase Ini Bukan Opsional

Ini proyek portfolio. Produk yang bagus tapi tidak bisa dipahami dalam 3 menit akan
dinilai sama dengan proyek biasa. Fase ini adalah tempat kerja product management
terlihat (PRD §17 metrik portfolio).

### 7.2 Deliverable

| Item | Isi |
|---|---|
| API Showcase | `components/showcase/` — request, response, diagram, tech stack, catatan keputusan (`content-schema.md` §B.10) |
| README | Problem, solusi, arsitektur, cara jalankan, contoh API, keputusan teknis, trade-off |
| Diagram arsitektur | Dari `technical-architecture.md` §33, dirender untuk dibaca cepat |
| Studi kasus produk | Masalah → insight → keputusan scope → hasil (PRD §25) |
| Screenshot/GIF | Alur utama: input → hasil → detail |
| Docker | `docker-compose.yml` (service `web`, `api`) |
| Deploy | Web ke Vercel, API ke container/server |
| E2E | Playwright: alur input → hasil → detail |

### 7.3 Exit Criteria

- [ ] README berisi: problem statement, cara menjalankan lokal (langkah lengkap dari
      clone sampai jalan), contoh request/response, diagram, keputusan teknis + alasan
- [ ] Setup instructions **diuji dari clone bersih** — bukan diasumsikan jalan
- [ ] API showcase di frontend menampilkan contoh yang **cocok** dengan response API nyata
- [ ] Catatan keputusan teknis tampil (kenapa deterministik, kenapa staple dikecualikan,
      kenapa JSON)
- [ ] Screenshot/GIF alur utama ada
- [ ] `docker compose up` menjalankan web + api, keduanya saling terhubung
- [ ] Web ter-deploy, API ter-deploy, demo live bekerja end-to-end
- [ ] `NEXT_PUBLIC_API_BASE_URL` menunjuk API production, CORS mengizinkan domain web
      production (bukan `*`)
- [ ] HTTPS aktif di kedua sisi
- [ ] Tidak ada secret di repo maupun di bundle frontend
- [ ] E2E Playwright hijau terhadap environment yang ter-deploy atau lokal
- [ ] CI hijau

### 7.4 Opsional (kerjakan bila ada nilai jelas)

- Rate limiting in-memory sederhana (jawaban PRD §26 Q6) — hanya bila API dipublikasikan
- Analytics anonim: jumlah request, empty-result rate, bahan tersering (PRD §14).
  Tanpa PII.

### 7.5 Risiko

| Risiko | Mitigasi |
|---|---|
| Contoh di showcase basi dan tidak cocok kontrak nyata | Idealnya generate dari integration test fixture (`content-schema.md` §B.10.2) |
| README mengasumsikan environment yang sudah ter-setup | Uji dari clone bersih |
| CORS dibuka `*` saat deploy demi cepat | Masuk exit criteria sebagai larangan eksplisit |
| Secret bocor ke bundle frontend | Hanya `NEXT_PUBLIC_*` yang boleh ke client. API key AI tetap server-side. |

---

## 8. Phase 7 — AI Enhancement (FUTURE)

**Status: TIDAK dikerjakan di MVP.** Dicatat agar arsitektur tidak menutup jalannya,
bukan sebagai pekerjaan terjadwal.

Dasar keputusan: PRD §10.3, §23 Decision 3, `technical-architecture.md` §13,
`component-architecture.md` §22–23.

### 8.1 Prasyarat Sebelum Fase Ini Boleh Dimulai

Semua harus terpenuhi:

- [ ] P1–P6 selesai dan ter-deploy
- [ ] Core MVP stabil, tidak ada bug terbuka di matching/ranking
- [ ] Ada kebutuhan nyata yang teridentifikasi — bukan "supaya ada AI-nya"
- [ ] Manfaat AI bisa dinyatakan sebagai perbaikan yang terukur

### 8.2 Cakupan Potensial

Urutan berdasarkan rasio nilai/kompleksitas:

1. **Natural language ingredient parsing** — `"2 telur, sisa ayam panggang"` →
   structured ingredients. Nilai paling jelas, ruang lingkup paling sempit.
2. **Recipe explanation** — kenapa resep ini cocok.
3. **Ingredient substitution** — saran pengganti bahan yang kurang.
4. **Conversational assistant** — paling kompleks, nilai paling belum terbukti.

### 8.3 Batasan Arsitektur (tidak bisa dinegosiasi)

- AI **hanya** menghasilkan atau mentransformasi data. Ranking tetap deterministik
  (`technical-architecture.md` §13).
- AI di balik interface `IngredientParser`, implementasi `ManualIngredientParser` /
  `AIIngredientParser`. Use case utama tidak berubah saat parser ditukar.
- Output AI **wajib** divalidasi ke schema internal sebelum dipakai
  (`component-architecture.md` §23).
- Matching engine tetap tidak boleh memanggil LLM (`AGENTS.md` §4).
- API key hanya di backend. `Frontend → OpenAI` dilarang
  (`technical-architecture.md` §17).
- Feature flag: AI bisa dimatikan dan produk tetap berfungsi penuh.

---

## 9. Traceability Kebutuhan Fungsional

Setiap FR dari PRD §13 dipetakan ke fase yang memenuhinya.

| FR | Kebutuhan | Fase |
|---|---|---|
| FR-01 | Input bahan manual | P4 (API), P5 (UI) |
| FR-02 | Normalisasi | P3 |
| FR-03 | Recipe matching | P3 |
| FR-04 | Ranking | P3 |
| FR-05 | Hingga 5 rekomendasi | P3 (limit), P4 (default/validasi) |
| FR-06 | Missing ingredients | P3 |
| FR-07 | Available ingredients | P3 |
| FR-08 | Detail resep | P2 (data), P4 (API), P5 (UI) |
| FR-09 | Validasi + error jelas | P4 |
| FR-10 | Demo interaktif pakai API nyata | P5 |
| FR-11 | Dokumentasi API + contoh | P4 (OpenAPI), P6 (README, showcase) |

Non-functional requirement (PRD §14):

| NFR | Fase |
|---|---|
| Performance p50/p95 | P4 (diukur di exit criteria) |
| Reliability / determinisme | P3 (test determinisme) |
| Maintainability / separation | P3, P4 (grep check dependency) |
| Security | P4 (validasi, CORS), P6 (HTTPS, secret) |
| Observability | P4 (logging), P6 (metrik opsional) |

---

## 10. Traceability Kriteria Penerimaan MVP

Dari PRD §18 — dipetakan ke fase yang menutupnya.

| Kriteria PRD §18 | Fase |
|---|---|
| User bisa input bahan manual | P5 |
| Request mencapai endpoint yang berfungsi | P4 |
| Bahan dinormalisasi konsisten | P3 |
| Engine mengurutkan deterministik | P3 |
| API mengembalikan hingga 5 rekomendasi | P4 |
| Tiap rekomendasi lengkap (match%, available, missing, waktu, difficulty, steps) | P4 |
| Frontend menampilkan response API nyata | P5 |
| Error API ditangani baik | P4, P5 |
| Automated test mencakup skenario matching utama | P3, P4 |
| Dokumentasi API + contoh | P4, P6 |
| Bisa dijalankan lokal via prosedur terdokumentasi | P6 |

Definition of Done teknis (`technical-architecture.md` §21):

| Item | Fase |
|---|---|
| API & frontend jalan lokal | P1, P6 |
| API contract terdokumentasi | P4 |
| Dataset ≥50 resep berkualitas | P2 (60 resep) |
| Matching engine punya unit test | P3 |
| API punya integration test | P4 |
| Frontend punya loading/error/empty state | P5 |
| Frontend pakai API nyata | P5 |
| Response schema tervalidasi | P4 |
| Health endpoint | P1, P4 |
| `.env.example` | P1 |
| README setup instructions | P6 |
| Tidak ada secret di source | P1, P6 |

---

## 11. Metrik per Fase

Cara menilai fase berhasil secara objektif — bukan hanya "selesai".

| Fase | Metrik | Target |
|---|---|---|
| P1 | CI hijau | Ya |
| P2 | Validator pass rate | 100% |
| P2 | Jumlah resep | 60 |
| P3 | Coverage `domain/` + `services/` | ≥90% |
| P3 | Test case `content-schema.md` lewat | 29/29 (14 normalisasi + 8 scoring + 7 ranking) |
| P3 | Determinisme | 2 run identik |
| P4 | Integration test skenario | 8/8 |
| P4 | Latency p50 / p95 | <200ms / <500ms |
| P5 | Component test state | 6/6 |
| P5 | `pnpm build` | Sukses |
| P6 | Setup dari clone bersih | Berhasil |
| P6 | E2E Playwright | Hijau |

---

## 12. Aturan Commit per Fase

Mengikuti `AGENTS.md` §7 — conventional commits, commit per task selesai, push manual.

| Fase | Scope commit yang umum |
|---|---|
| P1 | `chore(api)`, `chore(web)`, `chore(ci)` |
| P2 | `feat(data)`, `test(data)` |
| P3 | `feat(matching)`, `test(matching)` |
| P4 | `feat(api)`, `test(api)` |
| P5 | `feat(web)`, `test(web)` |
| P6 | `docs`, `chore(docker)`, `test(e2e)` |

---

## 13. Anti-Pattern Roadmap

Cara paling umum roadmap ini gagal:

1. **Melompat ke frontend sebelum API stabil.** Menghasilkan contract drift dan
   pekerjaan ganda.
2. **Menulis 60 resep sekaligus tanpa validasi.** Error referential integrity menumpuk,
   perbaikan jadi mahal.
3. **Menunda test sampai "nanti".** Di P3 test adalah spesifikasi, bukan formalitas.
4. **Menganggap exit criteria sebagai saran.** Kalau boleh dilewati, fase kehilangan
   fungsi sebagai gate.
5. **Menambah scope di tengah fase.** Ide baru masuk backlog V1.x, bukan fase yang
   sedang berjalan.
6. **Mengerjakan P7 AI karena terasa menarik.** PRD §23 Decision 3 eksplisit: AI hanya
   untuk masalah yang manfaatnya jelas.
7. **Tuning formula scoring untuk menutupi dataset lemah.** Perbaiki dataset.

---

## 14. Ringkasan Alur Nilai

```text
Input bahan
     ↓  P3 normalisasi
Canonical ingredients
     ↓  P3 matching + P2 dataset
Skor kecocokan
     ↓  P3 ranking
Urutan relevansi
     ↓  P4 REST API
Kontrak yang bisa dipakai client apa pun
     ↓  P5 frontend
Keputusan memasak
     ↓  P6 portfolio
Dipahami reviewer
```

Setiap fase menambah satu lapisan nilai di atas lapisan sebelumnya. Tidak ada fase yang
bisa dilewati tanpa merusak lapisan di atasnya.
