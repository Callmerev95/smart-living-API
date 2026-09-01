# Implementation Task Breakdown — Smart Living API

**Versi:** 1.0
**Status:** Draf Implementasi MVP
**Dokumen Terkait:** `prd.md`, `technical-architecture.md`, `component-architecture.md`, `content-schema.md`, `development-roadmap.md`
**Tujuan Dokumen:** Memecah MVP menjadi task konkret per file/komponen, lengkap dengan
dependency, acceptance criteria, dan test yang harus lulus — sehingga bisa dieksekusi
satu per satu oleh developer maupun AI agent tanpa menebak.

---

## 0. Cara Membaca & Mengeksekusi

### 0.1 Format Task

```text
T-P3-05 · Scoring function
  Fase     : 3
  Depends  : T-P3-01, T-P2-01
  File     : apps/api/app/domain/matching/scoring.py
  Test     : apps/api/tests/unit/test_scoring.py
  Deskripsi: apa yang dibuat
  Acceptance:
    - kriteria terverifikasi
  Done: perintah yang harus lulus
```

- **ID** — `T-P<fase>-<nomor>`. Dipakai di commit message.
- **Depends** — task yang wajib selesai lebih dulu. `—` berarti tidak ada.
- **File** — file utama yang dibuat/diubah. Bukan daftar lengkap, tapi lokasi tanggung jawab.
- **Acceptance** — kriteria biner. Kalau tidak bisa diverifikasi, bukan acceptance criteria.
- **Done** — perintah yang dijalankan untuk membuktikan task selesai.

### 0.2 Aturan Eksekusi

1. Kerjakan berurutan dalam satu fase. Task dengan `Depends` yang sama boleh paralel.
2. **Satu task = satu commit** (`AGENTS.md` §7). Push manual.
3. Sebelum menandai selesai: jalankan perintah di `Done`. Bukan asumsi.
4. Jangan lompat fase. Exit criteria fase ada di `development-roadmap.md`.
5. Butuh dokumentasi library → pakai `context7` (`AGENTS.md` §6).
6. Ragu soal kontrak data → `content-schema.md` adalah sumber resmi, termasuk
   Contract Delta v1.1 (§A.9).

### 0.3 Ringkasan Jumlah Task

| Fase | Task | Fokus |
|---|---|---|
| P1 Foundation | 12 | Tooling, config, CI, git |
| P2 Data | 11 | Model domain, dataset, repository |
| P3 Core Engine | 13 | Normalisasi, scoring, matching, ranking, service |
| P4 API | 16 | Schema, route, error, logging, integration test |
| P5 Frontend | 19 | Types, API client, hook, component, state, test |
| P6 Portfolio | 13 | Showcase, README, Docker, E2E, deploy |
| **Total** | **84** | |

### 0.4 Konvensi Path

Semua path relatif ke root repo. Prefix yang sering dipakai:

```text
apps/api/app/      backend source
apps/api/tests/    backend test
apps/web/          frontend source
data/recipes/      dataset
docs/              dokumentasi
```

---
---

# PHASE 1 — FOUNDATION

**Goal fase:** repo bisa dijalankan, di-lint, di-test. Belum ada fitur.
**Exit criteria:** `development-roadmap.md` §2.3.

---

### T-P1-01 · Struktur folder root

```text
Fase     : 1
Depends  : —
File     : (struktur direktori), .gitignore
```

**Deskripsi:** Buat skeleton folder sesuai `technical-architecture.md` §4 dan
`component-architecture.md` §4. Folder kosong diberi `.gitkeep` agar ter-track git.

Struktur yang dibuat:
```text
apps/api/, apps/web/, data/recipes/, docker/, .github/workflows/
```

**Acceptance:**
- Semua folder di atas ada
- `.gitignore` root memuat: `.venv`, `__pycache__`, `*.pyc`, `node_modules`, `.next`,
  `.env`, `.env.local`, `dist`, `build`, `.DS_Store`, `*.log`, `.pytest_cache`,
  `.ruff_cache`, `coverage`
- `docs/` sudah berisi 6 dokumen (prd, technical-architecture, component-architecture,
  content-schema, development-roadmap, implementation-task-breakdown)
- `AGENTS.md` ada di root

**Done:** `git status` menampilkan struktur, tidak ada folder tak terduga.

---

### T-P1-02 · Init project backend (uv)

```text
Fase     : 1
Depends  : T-P1-01
File     : apps/api/pyproject.toml
```

**Deskripsi:** Inisiasi project Python dengan `uv`. Python 3.12. Tambah dependency
runtime: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`. Dev:
`pytest`, `pytest-cov`, `httpx` (untuk TestClient), `ruff`.

**Versi di-pin eksplisit**, bukan range terbuka. Cek versi terbaru yang kompatibel
lewat `context7` sebelum menulis — jangan tebak dari ingatan.

**Acceptance:**
- `pyproject.toml` ada, `requires-python = ">=3.12"`
- Semua dependency ter-pin ke versi eksak
- `uv sync` berhasil membuat `.venv`
- `uv.lock` ter-commit
- `.venv` tidak ter-commit

**Done:** `uv sync && uv run python -c "import fastapi, pydantic; print('ok')"`

---

### T-P1-03 · Konfigurasi ruff

```text
Fase     : 1
Depends  : T-P1-02
File     : apps/api/pyproject.toml (section [tool.ruff])
```

**Deskripsi:** Konfigurasi ruff sebagai linter + formatter. Aktifkan rule set yang
berguna tanpa berlebihan: `E`, `F`, `I` (import sort), `UP` (pyupgrade), `B` (bugbear),
`SIM`. Line length 100.

**Acceptance:**
- `[tool.ruff]` ada di `pyproject.toml`
- `target-version = "py312"`
- Rule `I` aktif — import terurut otomatis
- `ruff check .` clean pada kode yang ada
- `ruff format --check .` clean

**Done:** `uv run ruff check . && uv run ruff format --check .`

---

### T-P1-04 · Konfigurasi pytest + smoke test

```text
Fase     : 1
Depends  : T-P1-02
File     : apps/api/pyproject.toml ([tool.pytest.ini_options]), apps/api/tests/
Test     : apps/api/tests/test_smoke.py
```

**Deskripsi:** Setup pytest dengan struktur `tests/unit/` dan `tests/integration/`.
Konfigurasi coverage untuk `app/`. Buat satu smoke test trivial untuk membuktikan
pipeline test jalan.

**Acceptance:**
- `tests/unit/` dan `tests/integration/` ada dengan `__init__.py`
- `testpaths = ["tests"]` terkonfigurasi
- Coverage source diarahkan ke `app/`
- Smoke test hijau

**Done:** `uv run pytest -v`

---

### T-P1-05 · Config & environment

```text
Fase     : 1
Depends  : T-P1-02
File     : apps/api/app/core/config.py, .env.example
Test     : apps/api/tests/unit/test_config.py
```

**Deskripsi:** `Settings` berbasis `pydantic-settings`, memuat semua konstanta dari
`content-schema.md` §A.7 plus config server.

Field wajib:
```text
api_port                       default 8000
cors_origins                   default ["http://localhost:3000"]
default_limit                  default 5
max_limit                      default 10
min_match_threshold            default 30
max_ingredients_per_request    default 30
max_ingredient_name_length     default 60
recipes_path                   default data/recipes/recipes.json
ingredients_path               default data/recipes/ingredients.json
log_level                      default INFO
```

**Acceptance:**
- Semua field di atas ada dengan default sesuai `content-schema.md` §A.7
- Bisa di-override lewat environment variable
- `.env.example` memuat semua variabel termasuk `OPENAI_API_KEY=` kosong
  (technical-architecture §22)
- `cors_origins` **tidak** default ke `["*"]`
- Path dataset resolve benar relatif ke root repo, bukan ke cwd
- Test: default values benar, override env terbaca

**Done:** `uv run pytest tests/unit/test_config.py -v`

---

### T-P1-06 · FastAPI app + CORS + router skeleton

```text
Fase     : 1
Depends  : T-P1-05
File     : apps/api/app/main.py, apps/api/app/api/v1/router.py
```

**Deskripsi:** Buat aplikasi FastAPI dengan metadata (title, description, version),
CORS middleware dari `settings.cors_origins`, dan router `v1` yang di-include dengan
prefix `/api/v1`.

Konsultasi `context7` untuk API `CORSMiddleware` dan `FastAPI()` metadata pada versi
yang di-pin di T-P1-02.

**Acceptance:**
- `app = FastAPI(...)` dengan title & version terisi
- CORS dibaca dari settings, bukan hardcode
- CORS **tidak** `allow_origins=["*"]`
- Router `v1` ter-include dengan prefix `/api/v1`
- `uv run uvicorn app.main:app` start tanpa error
- `/docs` bisa dibuka

**Done:** start server, buka `/docs`, pastikan render.

---

### T-P1-07 · Health endpoint (versi minimal)

```text
Fase     : 1
Depends  : T-P1-06
File     : apps/api/app/api/v1/routes/health.py
Test     : apps/api/tests/integration/test_health.py
```

**Deskripsi:** Endpoint `GET /api/v1/health` yang mengembalikan `{"status": "ok"}`.
Field `recipeCount`/`ingredientCount` ditambahkan nanti di T-P4-13 setelah repository ada.

**Acceptance:**
- `GET /api/v1/health` → `200`, body `{"status": "ok"}`
- Integration test pakai `TestClient` hijau
- Route tidak mengakses file dataset (belum ada)

**Done:** `uv run pytest tests/integration/test_health.py -v`

---

### T-P1-08 · Init project frontend (Next.js)

```text
Fase     : 1
Depends  : T-P1-01
File     : apps/web/package.json, apps/web/tsconfig.json, apps/web/app/
```

**Deskripsi:** Inisiasi Next.js + TypeScript dengan `pnpm`. App Router. Strict mode
TypeScript aktif.

Cek versi Next.js terbaru yang stabil lewat `context7` sebelum init. Pin versi eksak
di `package.json`.

**Acceptance:**
- `pnpm install` berhasil
- `tsconfig.json` dengan `"strict": true`
- App Router (`app/`), bukan Pages Router
- `pnpm dev` jalan, halaman render
- `pnpm build` sukses
- Script tersedia: `dev`, `build`, `start`, `lint`, `typecheck`, `test`
- `node_modules` tidak ter-commit, `pnpm-lock.yaml` ter-commit

**Done:** `pnpm install && pnpm typecheck && pnpm build`

---

### T-P1-09 · Tailwind CSS

```text
Fase     : 1
Depends  : T-P1-08
File     : apps/web/ (config Tailwind), apps/web/app/globals.css
```

**Deskripsi:** Setup Tailwind CSS. Cek metode instalasi yang benar untuk versi Tailwind
dan Next.js yang dipakai lewat `context7` — cara setup berubah antar versi major.

**Acceptance:**
- Tailwind aktif, utility class berpengaruh pada render
- `globals.css` ter-import di root layout
- `pnpm build` masih sukses
- Tidak ada CSS framework lain yang ikut terpasang

**Done:** `pnpm build`, lalu verifikasi visual satu utility class (mis. `text-red-500`).

---

### T-P1-10 · Vitest + React Testing Library

```text
Fase     : 1
Depends  : T-P1-08
File     : apps/web/vitest.config.ts, apps/web/tests/setup.ts
Test     : apps/web/tests/smoke.test.tsx
```

**Deskripsi:** Setup Vitest dengan environment `jsdom`, React Testing Library, dan
`@testing-library/jest-dom` matcher. Buat smoke test yang merender komponen trivial.

Cek konfigurasi Vitest + RTL untuk Next.js App Router lewat `context7`.

**Acceptance:**
- `pnpm test` jalan dan hijau
- Environment `jsdom` aktif
- Matcher `toBeInTheDocument` tersedia
- Path alias (`@/`) resolve di test sama seperti di build

**Done:** `pnpm test`

---

### T-P1-11 · GitHub Actions CI

```text
Fase     : 1
Depends  : T-P1-04, T-P1-10
File     : .github/workflows/ci.yml
```

**Deskripsi:** Workflow CI untuk push & pull request ke `main`. Dua job paralel:
`api` dan `web`.

Job `api`: setup Python 3.12 + uv → `uv sync` → `ruff check` → `ruff format --check`
→ `pytest`.
Job `web`: setup Node + pnpm → `pnpm install --frozen-lockfile` → `lint` → `typecheck`
→ `test` → `build`.

**Acceptance:**
- Trigger pada `push` dan `pull_request` ke `main`
- Dua job terpisah dengan working-directory masing-masing
- Dependency cache aktif (uv & pnpm)
- Versi action di-pin (bukan `@master`)
- Tidak ada secret yang dibutuhkan untuk CI lewat
- CI hijau di GitHub

**Done:** push, lalu `gh run list` menunjukkan status sukses.

---

### T-P1-12 · Git repository & remote

```text
Fase     : 1
Depends  : T-P1-01
File     : (git metadata)
```

**Deskripsi:** Inisiasi git, commit awal, buat repo GitHub publik, set remote `origin`.

Urutan langkah:

1. `brew install gh` (bila belum ada)
2. `gh auth login` — interaktif, butuh input user di terminal
3. `git config user.name` dan `git config user.email`
4. `git init -b main` (bila belum)
5. Periksa `git status` — pastikan tidak ada `.env`, `node_modules`, `.venv` ter-stage
6. `git add . && git commit -m "chore: initial project structure & docs"`
7. `gh repo create smart-living-API --public --source=. --remote=origin --push`

**Acceptance:**
- `git log` punya minimal 1 commit
- Branch utama bernama `main`
- Remote `origin` mengarah ke `smart-living-API`
- Repo visibility public
- Tidak ada secret, `.env`, `node_modules`, `.venv`, `.DS_Store` di history
- `git status` clean setelah commit

**Done:** `git log --oneline`, `git remote -v`, `gh repo view --json visibility`

**Catatan:** langkah 2 dan 7 butuh interaksi/kredensial user. Agent tidak melakukan
push otomatis (`AGENTS.md` §7).

---
---

# PHASE 2 — DATA

**Goal fase:** dataset 60 resep + ~120 ingredient valid, ter-load lewat repository.
**Exit criteria:** `development-roadmap.md` §3.4.

---

### T-P2-01 · Domain model Ingredient

```text
Fase     : 2
Depends  : T-P1-02
File     : apps/api/app/domain/models/ingredient.py
Test     : apps/api/tests/unit/test_domain_models.py
```

**Deskripsi:** Dataclass `Ingredient` sesuai `content-schema.md` §A.2.2. Frozen
(immutable). Enum `IngredientCategory` untuk 9 kategori di §A.2.3.

Field: `name`, `display_name`, `aliases`, `category`, `staple`.

**Acceptance:**
- Pakai `@dataclass(frozen=True)` — **bukan** `BaseModel`
- **Tidak ada** import `pydantic`, `fastapi`, atau library eksternal apa pun
- Hanya standard library (`dataclasses`, `enum`)
- `IngredientCategory` memuat 9 nilai §A.2.3
- Naming internal `snake_case` (`display_name`), mapping ke `displayName` terjadi di
  repository/schema — bukan di domain
- Test: instansiasi, immutability (assign → raise), enum valid

**Done:** `uv run pytest tests/unit/test_domain_models.py -v` dan
`grep -rn "pydantic\|fastapi" app/domain/` kosong.

---

### T-P2-02 · Domain model Recipe

```text
Fase     : 2
Depends  : T-P2-01
File     : apps/api/app/domain/models/recipe.py
Test     : apps/api/tests/unit/test_domain_models.py
```

**Deskripsi:** Dataclass `Recipe` dan `RecipeIngredient` sesuai `content-schema.md`
§A.3.2 dan §A.3.3. Enum `Difficulty` (`easy`/`medium`/`hard`).

`Recipe`: `id`, `name`, `description`, `ingredients`, `cooking_time_minutes`,
`difficulty`, `servings`, `steps`, `tags`, `source`.
`RecipeIngredient`: `name`, `required`.

Tambah helper murni (tanpa I/O):
```text
required_ingredient_names() -> tuple[str, ...]
all_ingredient_names()      -> tuple[str, ...]
```

**Acceptance:**
- Frozen dataclass, standard library saja
- **Tidak ada** field `quantity`/`unit` (out of scope MVP — `content-schema.md` §A.3.3)
- Helper mempertahankan **urutan** `ingredients[]` (dibutuhkan determinisme
  `content-schema.md` §A.5.3)
- Helper tidak melakukan filter staple — itu tanggung jawab scoring, bukan model
- Test: helper mengembalikan urutan benar, optional ingredient tidak masuk
  `required_ingredient_names()`

**Done:** `uv run pytest tests/unit/test_domain_models.py -v`

---

### T-P2-03 · Validator dataset

```text
Fase     : 2
Depends  : T-P2-02
File     : apps/api/scripts/validate_dataset.py
Test     : apps/api/tests/unit/test_validate_dataset.py
```

**Deskripsi:** Script CLI yang memvalidasi `ingredients.json` + `recipes.json` terhadap
**semua** aturan `content-schema.md` §A.2.4 dan §A.3.7. Exit code non-zero bila gagal,
dengan pesan yang menyebut file, index, dan aturan yang dilanggar.

Cek yang wajib diimplementasikan:

Ingredients (§A.2.4):
1. `name` unik
2. Tidak ada alias duplikat lintas ingredient
3. Tidak ada alias yang sama dengan `name` ingredient lain
4. Semua alias lowercase & trimmed
5. `category` valid enum
6. Minimal 1 staple

Recipes (§A.3.7):
1. `id` unik, format `recipe_NNN`
2. **Referential integrity** — setiap `ingredients[].name` ada di `ingredients.json`
3. Tidak ada ingredient duplikat dalam satu resep
4. Minimal 2 required non-staple per resep
5. `3 <= len(steps) <= 10`
6. `0 < cooking_time_minutes <= 180`
7. `difficulty` valid enum
8. `servings > 0`
9. `1 <= len(tags) <= 5`
10. `source` non-empty

Plus laporan ringkas (bukan error): jumlah resep, jumlah ingredient, distribusi
difficulty, distribusi waktu, top-10 ingredient tersering.

**Acceptance:**
- Semua 16 cek di atas terimplementasi
- Exit code `0` bila valid, `1` bila ada pelanggaran
- Pesan error menyebut lokasi spesifik (`recipes.json[12].ingredients[3]`)
- Melaporkan **semua** pelanggaran sekaligus, bukan berhenti di error pertama
- Test dengan fixture sengaja rusak: alias duplikat, ingredient tak terdaftar,
  steps < 3, semua-required-staple, id duplikat
- Bisa dijalankan sebagai `uv run python scripts/validate_dataset.py`

**Done:** `uv run pytest tests/unit/test_validate_dataset.py -v`

**Catatan:** task ini dibuat **sebelum** dataset agar setiap batch bisa langsung
divalidasi (`development-roadmap.md` §3.3).

---

### T-P2-04 · ingredients.json — fondasi bahan umum

```text
Fase     : 2
Depends  : T-P2-03
File     : data/recipes/ingredients.json
```

**Deskripsi:** Batch pertama kamus bahan: ~40 ingredient yang paling sering dipakai
masakan Indonesia sehari-hari, plus semua staple.

Wajib termasuk:
- Staple (5–8): `salt`, `cooking_oil`, `water`, `pepper`, `sugar`
- Protein umum: `egg`, `chicken`, `tofu`, `tempeh`
- Aromatik: `garlic`, `shallot`, `onion`, `chili`, `ginger`
- Sayur dasar: `carrot`, `cabbage`, `spinach`, `tomato`, `long_bean`
- Grain: `rice`, `noodle`
- Condiment: `soy_sauce`, `oyster_sauce`

Alias mengikuti panduan `content-schema.md` §A.2.5 — sertakan varian Indonesia, typo
umum, plural Inggris, bentuk spesifik.

**Acceptance:**
- ~40 ingredient, format sesuai §A.2.1
- 5–8 dengan `staple: true`
- Setiap ingredient punya minimal 1 alias bahasa Indonesia
- `canonical name` bahasa Inggris lowercase/snake_case
- `displayName` bahasa Indonesia Title Case
- Validator lewat 100%

**Done:** `uv run python scripts/validate_dataset.py`

---

### T-P2-05 · recipes.json — batch 1 (15 resep)

```text
Fase     : 2
Depends  : T-P2-04
File     : data/recipes/recipes.json
```

**Deskripsi:** 15 resep pertama, `recipe_001`–`recipe_015`. Fokus bahan paling umum
(telur, ayam, tahu, tempe, nasi, sayur dasar) agar overlap tinggi sejak awal.

Ikuti `content-schema.md`: §A.3 skema, §A.3.5 aturan steps, §A.3.6 vocabulary tags,
§A.8.2 komposisi yang disengaja, §A.8.5 anti-karang.

**Acceptance:**
- 15 resep, id `recipe_001`–`recipe_015`
- Semua `source: "original"`
- Setiap resep punya ≥2 required non-staple
- Steps 3–10, kalimat imperatif, ada indikator selesai (bukan hanya durasi)
- Tidak ada nomor di dalam string step
- Ingredient baru (bila ada) sudah ditambahkan ke `ingredients.json` lebih dulu
- Validator lewat 100%
- Setiap resep masuk akal secara kuliner — bisa benar-benar dimasak

**Done:** `uv run python scripts/validate_dataset.py`

---

### T-P2-06 · recipes.json — batch 2 (15 resep)

```text
Fase     : 2
Depends  : T-P2-05
File     : data/recipes/recipes.json, data/recipes/ingredients.json
```

**Deskripsi:** `recipe_016`–`recipe_030`. Perluas protein (ikan, seafood, daging) dan
variasi sayur. Tambah ingredient baru ke kamus sesuai kebutuhan (~30 ingredient baru).

**Acceptance:**
- Total 30 resep, id berurutan tanpa lompatan
- Ingredient baru terdaftar sebelum dipakai
- **Overlap terjaga:** bahan umum dari batch 1 tetap muncul di batch ini
- Validator lewat 100%

**Done:** `uv run python scripts/validate_dataset.py`

---

### T-P2-07 · recipes.json — batch 3 (15 resep)

```text
Fase     : 2
Depends  : T-P2-06
File     : data/recipes/recipes.json, data/recipes/ingredients.json
```

**Deskripsi:** `recipe_031`–`recipe_045`. Variasi kuliner (chinese-indonesian, western
sederhana) dan naikkan porsi difficulty `medium`/`hard` agar mendekati distribusi target
§A.8.3.

**Acceptance:**
- Total 45 resep
- Ada resep `medium` dan `hard` dengan kriteria §A.3.4 terpenuhi (jumlah langkah/teknik
  sesuai, bukan label sembarangan)
- Variasi `cookingTimeMinutes` melebar
- Validator lewat 100%

**Done:** `uv run python scripts/validate_dataset.py`

---

### T-P2-08 · recipes.json — batch 4 (15 resep) & audit dataset

```text
Fase     : 2
Depends  : T-P2-07
File     : data/recipes/recipes.json, data/recipes/ingredients.json
```

**Deskripsi:** `recipe_046`–`recipe_060`. Isi celah kombinasi bahan yang belum tercakup,
lalu audit keseluruhan dataset terhadap target §A.8.1 dan §A.8.3.

**Acceptance:**
- Total **60 resep**, id `recipe_001`–`recipe_060`
- Total **~120 ingredient** kanonik
- Distribusi difficulty mendekati ~60% easy / ~30% medium / ~10% hard
- Distribusi waktu mendekati ~40% ≤15 menit / ~40% 16–30 / ~20% >30
- Rata-rata 6–9 ingredient per resep
- Laporan validator menunjukkan bahan umum muncul di banyak resep (overlap tinggi)
- Validator lewat 100%

**Done:** `uv run python scripts/validate_dataset.py` — periksa bagian laporan ringkas.

---

### T-P2-09 · Repository interface

```text
Fase     : 2
Depends  : T-P2-02
File     : apps/api/app/repositories/base.py
```

**Deskripsi:** Interface abstrak `RecipeRepository` dan `IngredientRepository` sesuai
`technical-architecture.md` §5.4 dan `component-architecture.md` §20.

```text
RecipeRepository:
    get_all() -> tuple[Recipe, ...]
    get_by_id(recipe_id: str) -> Recipe | None
    count() -> int

IngredientRepository:
    get_all() -> tuple[Ingredient, ...]
    get_by_name(name: str) -> Ingredient | None
    get_alias_map() -> Mapping[str, str]   # alias -> canonical
    count() -> int
```

**Acceptance:**
- Pakai `abc.ABC` + `@abstractmethod`
- Return type domain model, **bukan** dict atau `BaseModel`
- Tidak ada referensi ke JSON, file, atau database
- `get_alias_map()` ada di interface — normalizer bergantung pada abstraksi ini, bukan
  pada implementasi JSON
- Tidak ada method yang menyinggung ranking/scoring
  (`component-architecture.md` §25 Rule 5)

**Done:** `uv run ruff check .` dan verifikasi tidak ada import selain `abc`, `typing`,
domain models.

---

### T-P2-10 · JsonRecipeRepository

```text
Fase     : 2
Depends  : T-P2-09, T-P2-08
File     : apps/api/app/repositories/json_recipe_repository.py
Test     : apps/api/tests/unit/test_json_recipe_repository.py
```

**Deskripsi:** Implementasi `RecipeRepository` yang membaca `recipes.json`. Load sekali
saat inisialisasi (technical-architecture §16 — dataset dimuat saat startup), simpan
in-memory sebagai tuple. Mapping `camelCase` JSON → `snake_case` domain terjadi di sini.

**Acceptance:**
- Load sekali di `__init__`, bukan setiap `get_all()`
- `get_all()` mengembalikan 60 `Recipe`
- `get_by_id("recipe_001")` mengembalikan resep benar
- `get_by_id("nonexistent")` mengembalikan `None` — **bukan** raise
- `count()` mengembalikan 60
- Mapping `cookingTimeMinutes` → `cooking_time_minutes` benar
- `difficulty` string → enum `Difficulty`
- Urutan `get_all()` konsisten dengan urutan di file (determinisme)
- File tidak ada → raise error yang jelas saat init, bukan gagal silent
- JSON malformed → error yang menyebut file
- Repository **tidak** melakukan filtering/ranking

**Done:** `uv run pytest tests/unit/test_json_recipe_repository.py -v`

---

### T-P2-11 · JsonIngredientRepository

```text
Fase     : 2
Depends  : T-P2-09, T-P2-04
File     : apps/api/app/repositories/json_ingredient_repository.py
Test     : apps/api/tests/unit/test_json_ingredient_repository.py
```

**Deskripsi:** Implementasi `IngredientRepository` untuk `ingredients.json`. Selain
list ingredient, membangun **alias map** `alias → canonical` sekali saat init agar
lookup normalisasi O(1) (`content-schema.md` §A.4.4).

Alias map memuat: setiap `name` → dirinya sendiri, dan setiap `alias` → `name`.

**Acceptance:**
- `get_all()` mengembalikan ~120 `Ingredient`
- `get_by_name("egg")` benar, `get_by_name("telur")` → `None` (alias bukan name)
- `get_alias_map()["telur"] == "egg"`
- `get_alias_map()["egg"] == "egg"` — canonical juga ada di map
- Alias map dibangun sekali di `__init__`, bukan per call
- Alias duplikat → raise error saat init (fail fast, bukan silent overwrite)
- `count()` benar
- Lookup case: map dibangun dari alias yang sudah lowercase

**Done:** `uv run pytest tests/unit/test_json_ingredient_repository.py -v`

---
---

# PHASE 3 — CORE ENGINE

**Goal fase:** recommendation logic lengkap, deterministik, ter-unit-test, tanpa import
framework.
**Exit criteria:** `development-roadmap.md` §4.4 dan gate kualitas dataset §4.5.

**Aturan mutlak fase ini:** tidak ada satu pun file di `app/domain/` yang boleh import
`fastapi`, `pydantic`, `httpx`, `requests`, atau `openai`.

---

### T-P3-01 · Domain model MatchResult

```text
Fase     : 3
Depends  : T-P2-02
File     : apps/api/app/domain/models/match_result.py
Test     : apps/api/tests/unit/test_domain_models.py
```

**Deskripsi:** Frozen dataclass `MatchResult` sesuai `component-architecture.md` §17.

Field:
```text
recipe_id              str
match_percentage       int
available_ingredients  tuple[str, ...]
missing_ingredients    tuple[str, ...]
cooking_time_minutes   int      # dibawa untuk keperluan ranking tie-breaker
```

`cooking_time_minutes` disertakan agar `ranking.py` tidak perlu bergantung pada objek
`Recipe` — ranking hanya butuh sort key.

**Acceptance:**
- Frozen dataclass, standard library saja
- `missing_count` tersedia sebagai property (turunan `len(missing_ingredients)`),
  bukan field yang bisa tidak sinkron
- Tuple, bukan list — mendukung immutability & determinisme
- Tidak ada method yang menghitung skor (itu tugas `scoring.py`)

**Done:** `uv run pytest tests/unit/test_domain_models.py -v`

---

### T-P3-02 · Normalizer — tokenizer & cleanup

```text
Fase     : 3
Depends  : T-P1-02
File     : apps/api/app/services/ingredient_normalizer.py
Test     : apps/api/tests/unit/test_normalizer_tokenize.py
```

**Deskripsi:** Bagian pertama pipeline `content-schema.md` §A.4.1 langkah 1–4: split,
trim, lowercase, collapse whitespace. Fungsi murni, belum menyentuh kamus.

```text
tokenize(raw: str) -> tuple[str, ...]
```

Split pada koma **dan** newline. Token kosong dibuang.

**Acceptance:**
- `"telur,  ayam , wortel"` → `("telur", "ayam", "wortel")`
- `" TELUR "` → `("telur",)`
- `"telur, , ayam"` → `("telur", "ayam")` — token kosong dibuang
- `""` → `()`
- `"telur\nayam"` → `("telur", "ayam")`
- Whitespace ganda di dalam token dikompres: `"chicken   breast"` → `"chicken breast"`
- Pure function, tanpa dependency
- Menerima juga input berupa `list[str]` (kasus API menerima array) — setiap elemen
  di-tokenize lalu digabung

**Done:** `uv run pytest tests/unit/test_normalizer_tokenize.py -v`

---

### T-P3-03 · Normalizer — strip kuantitas & plural

```text
Fase     : 3
Depends  : T-P3-02
File     : apps/api/app/services/ingredient_normalizer.py
Test     : apps/api/tests/unit/test_normalizer_strip.py
```

**Deskripsi:** Pipeline langkah 5–6 (`content-schema.md` §A.4.2, §A.4.3).

```text
strip_quantity(token: str) -> str
strip_plural(token: str) -> str
```

Satuan yang dikenali: `gr`, `gram`, `kg`, `ml`, `l`, `liter`, `sdm`, `sdt`, `buah`,
`butir`, `siung`, `lembar`, `batang`, `ekor`, `potong`, `ikat`, `bungkus`, `pcs`,
`pieces`.

Angka: integer, desimal (`1.5`, `1,5`), pecahan (`1/2`).

**Acceptance:**
- `"2 eggs"` → `"eggs"`
- `"2 butir telur"` → `"telur"`
- `"1/2 wortel"` → `"wortel"`
- `"100 gr ayam"` → `"ayam"`
- `"3 sdm kecap"` → `"kecap"`
- `"250ml susu"` → `"susu"` (tanpa spasi antara angka dan satuan)
- `"1,5 kg ayam"` → `"ayam"`
- Kuantitas **dibuang, tidak disimpan** (out of scope MVP)
- Token yang bukan angka di awal tidak berubah: `"telur"` → `"telur"`
- Angka di tengah tidak dibuang: `"cabai 2 warna"` tidak jadi `"warna"` — hanya prefix
- `strip_plural("carrots")` → `"carrot"`
- `strip_plural("tomatoes")` → `"tomato"`
- `strip_plural("telur")` → `"telur"` (kata non-Inggris tidak dirusak)
- `strip_plural("rice")` → `"rice"` (jangan buang `e` dari kata yang berakhir `ce`)
- Pure function

**Done:** `uv run pytest tests/unit/test_normalizer_strip.py -v`

---

### T-P3-04 · Normalizer — lookup & IngredientNormalizer

```text
Fase     : 3
Depends  : T-P3-03, T-P2-11
File     : apps/api/app/services/ingredient_normalizer.py
Test     : apps/api/tests/unit/test_normalizer.py
```

**Deskripsi:** Kelas `IngredientNormalizer` yang menyatukan pipeline lengkap
`content-schema.md` §A.4.1. Menerima alias map lewat constructor (dependency injection),
bukan membaca file sendiri.

```text
class IngredientNormalizer:
    def __init__(self, alias_map: Mapping[str, str]): ...
    def normalize(self, raw) -> NormalizationResult
```

`NormalizationResult`: `canonical: tuple[str, ...]`, `unknown: tuple[str, ...]`,
`raw: tuple[str, ...]`.

Urutan lookup §A.4.4: exact `name` → exact alias → setelah plural-strip. Gagal semua →
`unknown`.

**Acceptance:**
- **Seluruh 14 test case `content-schema.md` §A.4.5 hijau** — ini spesifikasinya
- Dedupe canonical, urutan kemunculan pertama dipertahankan
- Dedupe juga berlaku untuk `unknown`
- Tidak fuzzy match, tidak menebak (§A.4.4)
- `raw` menyimpan input asli setelah lowercase+trim (untuk Delta 3)
- Normalizer **tidak** membaca file — alias map di-inject
- Lookup O(1) — tidak ada loop linear ke seluruh ingredient
- Tidak import `fastapi`/`pydantic`

**Done:** `uv run pytest tests/unit/test_normalizer.py -v`

---

### T-P3-05 · Scoring — pure function

```text
Fase     : 3
Depends  : T-P3-01
File     : apps/api/app/domain/matching/scoring.py
Test     : apps/api/tests/unit/test_scoring.py
```

**Deskripsi:** Fungsi murni perhitungan match percentage sesuai
`content-schema.md` §A.5.2 — **termasuk Delta 1 (staple exclusion)**.

```text
calculate_match_percentage(matched: int, denominator: int) -> int
```

Pembulatan half-up. `denominator == 0` → `0` (guard divide-by-zero).

**Acceptance:**
- `(3, 4)` → `75`
- `(0, 4)` → `0`
- `(4, 4)` → `100`
- `(2, 3)` → `67` (half-up, bukan `66`)
- `(1, 3)` → `33`
- `(1, 2)` → `50`
- `(0, 0)` → `0` **tanpa raise** `ZeroDivisionError`
- Output selalu `int` dalam rentang 0–100
- Pure function — tanpa I/O, tanpa state
- Tidak import apa pun selain standard library

**Done:** `uv run pytest tests/unit/test_scoring.py -v`

---

### T-P3-06 · Matching engine

```text
Fase     : 3
Depends  : T-P3-05, T-P2-02
File     : apps/api/app/domain/matching/engine.py
Test     : apps/api/tests/unit/test_matching_engine.py
```

**Deskripsi:** Inti produk. Menerapkan §A.5.1 himpunan, §A.5.2 formula, §A.5.3
available/missing — dengan staple exclusion (Delta 1).

```text
def match_recipe(
    user_ingredients: frozenset[str],
    recipe: Recipe,
    staple_names: frozenset[str],
) -> MatchResult

def match_recipes(
    user_ingredients, recipes, staple_names
) -> tuple[MatchResult, ...]
```

Staple diterima sebagai `frozenset[str]` — engine tidak perlu tahu objek `Ingredient`
maupun dari mana daftar itu berasal.

**Acceptance:**
- **Seluruh 8 test case `content-schema.md` §A.5.5 hijau** — termasuk case 4 & 5
  (staple exclusion) dan case 8 (semua-staple → 0, tanpa exception)
- `required: false` tidak masuk denominator, tidak masuk `missingIngredients` (case 7)
- Bahan user yang tidak dipakai resep tidak menurunkan skor (case 6)
- Staple **tidak** muncul di `availableIngredients` maupun `missingIngredients`
- Urutan `availableIngredients`/`missingIngredients` mengikuti urutan `ingredients[]`
  resep — **bukan** urutan iterasi set (determinisme, §A.5.3)
- Menerima `frozenset` untuk user ingredients (lookup O(1))
- `grep -n "fastapi\|pydantic\|httpx\|requests\|openai" engine.py` kosong
- Tidak melakukan sorting/ranking — itu `ranking.py`
- Tidak load file

**Done:** `uv run pytest tests/unit/test_matching_engine.py -v`

---

### T-P3-07 · Ranking

```text
Fase     : 3
Depends  : T-P3-01
File     : apps/api/app/domain/matching/ranking.py
Test     : apps/api/tests/unit/test_ranking.py
```

**Deskripsi:** Sorting deterministik sesuai `content-schema.md` §A.6 dan
`technical-architecture.md` §8.5.

```text
def rank(results: Sequence[MatchResult]) -> tuple[MatchResult, ...]
def filter_by_threshold(results, threshold: int) -> tuple[MatchResult, ...]
def apply_limit(results, limit: int) -> tuple[MatchResult, ...]
```

Sort key: `(-match_percentage, missing_count, cooking_time_minutes, recipe_id)`.

**Acceptance:**
- **Seluruh 7 test case `content-schema.md` §A.6.1 hijau**
- Tie-breaker berlapis bekerja dalam urutan benar: match% DESC → missing ASC →
  waktu ASC → id ASC
- `recipe_id` dibandingkan sebagai string (`recipe_002` < `recipe_005`)
- Determinisme: input teracak, `rank()` 2x → output identik
- `filter_by_threshold` dan `apply_limit` terpisah dari `rank` — agar urutan operasi
  (score → filter → sort → limit) dikendalikan service, bukan tersembunyi
- Tidak memodifikasi input (return tuple baru)
- Tidak import framework

**Done:** `uv run pytest tests/unit/test_ranking.py -v`

---

### T-P3-08 · RecommendationService

```text
Fase     : 3
Depends  : T-P3-04, T-P3-06, T-P3-07, T-P2-10, T-P2-11
File     : apps/api/app/services/recommendation_service.py
Test     : apps/api/tests/unit/test_recommendation_service.py
```

**Deskripsi:** Orchestration layer sesuai `component-architecture.md` §15. Menyusun
urutan operasi §A.6: **normalize → get recipes → score → filter → rank → limit**.

```text
class RecommendationService:
    def __init__(self, normalizer, recipe_repo, ingredient_repo, settings): ...
    def recommend(self, ingredients, limit=None) -> RecommendationResult
```

`RecommendationResult` (domain-level, bukan Pydantic): `raw`, `canonical`, `unknown`,
`results: tuple[MatchResult, ...]`, `limit`, `threshold`.

Staple names diturunkan dari `ingredient_repo` di sini, lalu diteruskan ke engine.

**Acceptance:**
- Urutan operasi benar: **filter threshold sebelum limit** (§A.6) — bukan limit dulu
- `limit=None` → pakai `settings.default_limit`
- `limit` di-clamp ke `settings.max_limit`
- Mengembalikan `unknown` dari normalizer (Delta 2)
- Mengembalikan `raw` dan `canonical` (Delta 3)
- Service **tidak** tahu format JSON — hanya bicara ke interface repository
  (`technical-architecture.md` §5.4)
- Service **tidak** menghitung match percentage sendiri — delegasi ke engine
- Service tidak import `fastapi`
- Test pakai **fake repository** (stub in-memory), bukan file nyata — service test harus
  cepat dan terisolasi
- Test: semua unknown → `results` kosong tanpa error; threshold memfilter; limit bekerja;
  input kosong → hasil kosong (validasi input adalah tanggung jawab API layer)

**Done:** `uv run pytest tests/unit/test_recommendation_service.py -v`

---

### T-P3-09 · Test determinisme

```text
Fase     : 3
Depends  : T-P3-08
File     : —
Test     : apps/api/tests/unit/test_determinism.py
```

**Deskripsi:** Test khusus yang membuktikan klaim inti produk: input sama → output
identik (PRD §14 Reliability, `technical-architecture.md` §8.5).

**Acceptance:**
- Jalankan `recommend()` dengan input sama 5x → hasil **identik**, termasuk urutan
  array `availableIngredients` dan `missingIngredients`
- Urutan input diacak (`["ayam","telur"]` vs `["telur","ayam"]`) → hasil ranking identik
- Urutan resep di repository diacak → hasil ranking identik
- Test dijalankan terhadap dataset **nyata** (60 resep), bukan fixture kecil
- Tidak ada ketergantungan pada urutan iterasi `set`/`dict`

**Done:** `uv run pytest tests/unit/test_determinism.py -v` — jalankan 3x, hasil sama.

---

### T-P3-10 · Benchmark kualitas dataset (gate P2↔P3)

```text
Fase     : 3
Depends  : T-P3-09
File     : apps/api/scripts/benchmark_recommendations.py
```

**Deskripsi:** Script yang menjalankan 5 kombinasi input `development-roadmap.md` §4.5
terhadap dataset nyata dan mencetak hasilnya. Ini **gate kualitas dataset**, bukan test
pass/fail otomatis — hasilnya dibaca manusia.

Output per input: jumlah hasil, sebaran match%, nama resep teratas, `unknown`.

**Acceptance:**
- `telur, ayam, wortel` → ≥3 hasil dengan **sebaran skor berbeda** (bukan semua 100%
  atau semua 0%)
- `tahu, tempe, kecap` → ≥3 hasil
- `nasi, telur, bawang putih` → ≥3 hasil
- `telur` (satu bahan) → ada hasil
- `kangkung, durian` → `results: []`, `unknown` terisi, **tanpa exception**
- Script mencetak laporan yang bisa dibaca, bukan hanya assert
- Hasil di-review manual: apakah ranking terasa relevan secara kuliner?

**Done:** `uv run python scripts/benchmark_recommendations.py` — baca output.

**Catatan:** kalau sebaran skor tidak muncul, **kembali ke P2** perbaiki overlap dataset.
Jangan tuning formula untuk menutupi (`development-roadmap.md` §4.6).

---

### T-P3-11 · Verifikasi dependency boundary

```text
Fase     : 3
Depends  : T-P3-10
File     : apps/api/tests/unit/test_architecture_boundary.py
```

**Deskripsi:** Test otomatis yang menegakkan aturan dependency `AGENTS.md` §4 —
sehingga pelanggaran tertangkap CI, bukan bergantung pada review manual.

Implementasi: baca file `.py` di `app/domain/`, parse import (AST atau regex), assert
tidak ada import terlarang.

**Acceptance:**
- Test gagal bila ada file di `app/domain/` yang import `fastapi`, `pydantic`,
  `httpx`, `requests`, `openai`, atau driver database
- Test gagal bila file di `app/api/` memanggil `open()` atau `json.load` langsung
  (route tidak boleh akses data — `component-architecture.md` §25 Rule 2)
- Pesan kegagalan menyebut file dan import yang melanggar
- Test ini jalan di CI

**Done:** `uv run pytest tests/unit/test_architecture_boundary.py -v`

---

### T-P3-12 · Coverage check

```text
Fase     : 3
Depends  : T-P3-11
File     : apps/api/pyproject.toml
```

**Deskripsi:** Konfigurasi threshold coverage untuk `app/domain/` dan `app/services/`
minimal 90% (`development-roadmap.md` §11). CI gagal bila di bawah.

**Acceptance:**
- `pytest --cov` melaporkan coverage `app/domain/` dan `app/services/` ≥90%
- Threshold ter-enforce (`fail_under`) — bukan hanya dilaporkan
- File yang wajar dikecualikan (`__init__.py`) dikonfigurasi eksplisit
- CI menjalankan coverage check

**Done:** `uv run pytest --cov=app --cov-report=term-missing`

---

### T-P3-13 · Composition root / dependency wiring

```text
Fase     : 3
Depends  : T-P3-08
File     : apps/api/app/core/dependencies.py
Test     : apps/api/tests/unit/test_dependencies.py
```

**Deskripsi:** Satu tempat yang membangun objek: repository → normalizer → service.
Dipakai FastAPI di P4 lewat `Depends`, tapi dibuat di P3 agar bisa diuji tanpa HTTP.

Repository & service di-instansiasi **sekali** (singleton), bukan per request —
dataset tidak boleh di-load ulang setiap request (`technical-architecture.md` §16).

**Acceptance:**
- Ada fungsi factory yang mengembalikan `RecommendationService` siap pakai
- Repository di-load sekali, di-cache
- Dataset tidak dibaca ulang per pemanggilan
- Bisa dipakai tanpa FastAPI (test langsung memanggil factory)
- Path dataset dari `settings`, bukan hardcode
- Test: 2x pemanggilan factory → instance repository sama

**Done:** `uv run pytest tests/unit/test_dependencies.py -v`

---
---

# PHASE 4 — API

**Goal fase:** REST API lengkap dengan validasi, error konsisten, OpenAPI docs.
**Exit criteria:** `development-roadmap.md` §5.3.

**Aturan mutlak fase ini:** route hanya request → validation → service call → response.
Tidak ada perhitungan match percentage di route.

---

### T-P4-01 · Base schema & alias generator

```text
Fase     : 4
Depends  : T-P1-02
File     : apps/api/app/schemas/base.py
Test     : apps/api/tests/unit/test_schema_base.py
```

**Deskripsi:** Base Pydantic model dengan `alias_generator` camelCase +
`populate_by_name=True`, sehingga field internal `snake_case` otomatis ter-serialize
sebagai `camelCase` (`AGENTS.md` §5).

Cek API `ConfigDict`, `alias_generator`, dan `to_camel` untuk Pydantic v2 lewat
`context7` — berbeda dari v1.

**Acceptance:**
- `cooking_time_minutes` ter-serialize sebagai `cookingTimeMinutes`
- `match_percentage` → `matchPercentage`
- Deserialisasi menerima **keduanya** (`populate_by_name`)
- Semua response schema mewarisi base ini — konsistensi tidak bergantung disiplin manual
- Test: round-trip serialize/deserialize

**Done:** `uv run pytest tests/unit/test_schema_base.py -v`

---

### T-P4-02 · Error schema & exception types

```text
Fase     : 4
Depends  : T-P4-01
File     : apps/api/app/schemas/error.py, apps/api/app/core/errors.py
Test     : apps/api/tests/unit/test_errors.py
```

**Deskripsi:** Format error `content-schema.md` §A.10.5 dan exception domain-level.

Schema: `ErrorDetail{code, message, details}`, `ErrorResponse{error}`.

Exception: `AppError` (base), `InvalidIngredientsError`, `RecipeNotFoundError`.
Masing-masing membawa `code` dan HTTP status.

Error code: `INVALID_INGREDIENTS`, `VALIDATION_ERROR`, `RECIPE_NOT_FOUND`,
`INGREDIENT_NOT_FOUND`, `INTERNAL_ERROR`.

**Acceptance:**
- Struktur response tepat `{"error": {"code", "message", "details"}}`
- 5 error code terdefinisi sebagai enum/konstanta, bukan string literal tersebar
- Mapping code → HTTP status sesuai tabel §A.10.5
- Exception domain **tidak** import `fastapi` — hanya membawa data. Konversi ke HTTP
  terjadi di handler (T-P4-03)
- `details` opsional, default `None`

**Done:** `uv run pytest tests/unit/test_errors.py -v`

---

### T-P4-03 · Global exception handler

```text
Fase     : 4
Depends  : T-P4-02, T-P1-06
File     : apps/api/app/main.py, apps/api/app/core/errors.py
Test     : apps/api/tests/integration/test_error_handling.py
```

**Deskripsi:** Handler yang mengubah exception menjadi response error konsisten.
Tiga handler: `AppError`, `RequestValidationError` (Pydantic → `VALIDATION_ERROR` 422),
`Exception` (→ `INTERNAL_ERROR` 500).

**Acceptance:**
- `AppError` → status & code sesuai definisi exception
- Pydantic validation error → 422 dengan `code: "VALIDATION_ERROR"`, `details` memuat
  ringkasan field yang salah
- Unhandled exception → 500 `INTERNAL_ERROR`
- **Tidak ada stack trace di response** — diverifikasi dengan endpoint test yang
  sengaja raise
- Stack trace tetap masuk log server (bukan hilang)
- Semua response error mengikuti format §A.10.5, tanpa kecuali

**Done:** `uv run pytest tests/integration/test_error_handling.py -v`

---

### T-P4-04 · Request schema recommendations

```text
Fase     : 4
Depends  : T-P4-01
File     : apps/api/app/schemas/recommendation.py
Test     : apps/api/tests/unit/test_schema_recommendation.py
```

**Deskripsi:** `RecommendationRequest` dengan validasi `content-schema.md` §A.10.1.

```text
ingredients: list[str]   min 1 item
limit: int | None        default None, 1..max_limit
```

**Acceptance:**
- `ingredients` wajib; hilang → validation error
- List kosong `[]` → ditolak
- List berisi hanya string kosong/whitespace → ditolak (`INVALID_INGREDIENTS`)
- Lebih dari `max_ingredients_per_request` (30) → ditolak
- Item lebih dari `max_ingredient_name_length` (60) → ditolak
- `limit=0` → ditolak; `limit=11` → ditolak; `limit` absen → `None`
- Batas diambil dari `settings`, bukan angka hardcode di schema
- Test tiap kasus di atas

**Done:** `uv run pytest tests/unit/test_schema_recommendation.py -v`

---

### T-P4-05 · Response schema recommendations (Delta v1.1)

```text
Fase     : 4
Depends  : T-P4-04
File     : apps/api/app/schemas/recommendation.py
Test     : apps/api/tests/unit/test_schema_recommendation.py
```

**Deskripsi:** Response schema **persis** sesuai `content-schema.md` §A.10.1 —
termasuk ketiga Delta v1.1.

```text
QuerySchema             raw, ingredients
RecommendationItem      id, name, description, matchPercentage,
                        availableIngredients, missingIngredients,
                        cookingTimeMinutes, difficulty, servings,
                        ingredients, steps, tags
MetaSchema              count, limit, threshold
RecommendationResponse  query, unknownIngredients, results, meta
```

**Acceptance:**
- `query.raw` ada (Delta 3)
- `query.ingredients` ada, berisi canonical (Delta 3)
- `unknownIngredients` ada di **root** response, tipe `list[str]`, default `[]` (Delta 2)
- `meta` memuat `count`, `limit`, `threshold`
- Semua field ter-serialize `camelCase`
- `RecommendationItem.ingredients` = daftar **lengkap** bahan resep (termasuk optional &
  staple) — beda dari `availableIngredients` (§A.5.4)
- JSON hasil serialize dibandingkan struktur-per-struktur dengan contoh §A.10.1 di test
- `difficulty` ter-serialize sebagai string enum value

**Done:** `uv run pytest tests/unit/test_schema_recommendation.py -v`

---

### T-P4-06 · Schema recipe & ingredient

```text
Fase     : 4
Depends  : T-P4-01
File     : apps/api/app/schemas/recipe.py, apps/api/app/schemas/ingredient.py
Test     : apps/api/tests/unit/test_schema_recipe.py
```

**Deskripsi:** Schema untuk `GET /recipes/{id}` (§A.10.2) dan `GET /ingredients`
(§A.10.3).

`RecipeResponse`: semua field resep, **tanpa** `matchPercentage`/`availableIngredients`/
`missingIngredients` — field itu hanya bermakna dalam konteks query.

`IngredientItem` + `IngredientListResponse{ingredients, meta}`.

**Acceptance:**
- `RecipeResponse` tidak punya field match-related (§A.10.2)
- `RecipeResponse.ingredients` memuat `name` + `required` per item
- `IngredientItem` memuat `name`, `displayName`, `aliases`, `category`, `staple`
- Serialisasi `camelCase`
- Ada mapper domain → schema yang eksplisit (bukan `**recipe.__dict__`)

**Done:** `uv run pytest tests/unit/test_schema_recipe.py -v`

---

### T-P4-07 · Mapper domain → schema

```text
Fase     : 4
Depends  : T-P4-05, T-P4-06
File     : apps/api/app/schemas/mappers.py
Test     : apps/api/tests/unit/test_mappers.py
```

**Deskripsi:** Fungsi eksplisit yang mengubah objek domain (`RecommendationResult`,
`MatchResult`, `Recipe`, `Ingredient`) menjadi response schema.

Ini yang menjaga domain tetap bebas Pydantic: konversi terjadi di boundary, bukan dengan
membuat domain model mewarisi `BaseModel`.

```text
to_recommendation_response(result, recipe_lookup) -> RecommendationResponse
to_recipe_response(recipe) -> RecipeResponse
to_ingredient_list_response(ingredients) -> IngredientListResponse
```

**Acceptance:**
- Mapper menggabungkan `MatchResult` (skor) dengan `Recipe` (nama, steps, dll) —
  `MatchResult` sengaja tidak menyimpan data resep lengkap
- Urutan `results` dari service dipertahankan (jangan re-sort di mapper)
- `unknownIngredients` diteruskan apa adanya
- `meta.count` = `len(results)` setelah filter & limit
- `meta.threshold` = threshold yang benar-benar dipakai
- Mapper adalah fungsi murni — tanpa akses repository/file
- Test: satu `RecommendationResult` lengkap → JSON cocok struktur §A.10.1

**Done:** `uv run pytest tests/unit/test_mappers.py -v`

---

### T-P4-08 · Route POST /recommendations

```text
Fase     : 4
Depends  : T-P4-07, T-P4-03, T-P3-13
File     : apps/api/app/api/v1/routes/recommendations.py
Test     : apps/api/tests/integration/test_recommendations.py
```

**Deskripsi:** Endpoint utama. Route tipis sesuai `component-architecture.md` §35 "Good":
terima request tervalidasi → panggil service lewat `Depends` → map ke response.

**Acceptance:**
- `POST /api/v1/recommendations` → 200 untuk input valid
- Response cocok kontrak §A.10.1 (dibandingkan struktur di test)
- Route **tidak** menghitung apa pun — hanya delegasi
- Service diperoleh lewat `Depends`, bukan import global/instansiasi di route
- `response_model` diset agar OpenAPI akurat
- `grep -n "load_json\|open(\|json.load" recommendations.py` kosong
- Contoh request/response terdaftar di OpenAPI (`openapi_examples` atau `json_schema_extra`)
- Test: input valid → hasil masuk akal terhadap dataset nyata

**Done:** `uv run pytest tests/integration/test_recommendations.py -v`

---

### T-P4-09 · Integration test — validasi request

```text
Fase     : 4
Depends  : T-P4-08
File     : —
Test     : apps/api/tests/integration/test_recommendations_validation.py
```

**Deskripsi:** Menutup 8 skenario `development-roadmap.md` §5.3 dan
`technical-architecture.md` §20.2.

| Skenario | Ekspektasi |
|---|---|
| Input valid | 200, `results` terisi |
| `ingredients: []` | 400 `INVALID_INGREDIENTS` |
| Field `ingredients` hilang | 422 `VALIDATION_ERROR` |
| `limit: 0` | 422 |
| `limit: 11` | 422 |
| `limit: "abc"` | 422 |
| Unknown ingredient | **200**, `unknownIngredients` terisi (Delta 2) |
| Tidak ada resep cocok | 200, `results: []` |
| 31 bahan | 400 |
| Nama bahan 61 karakter | 400 |

**Acceptance:**
- Semua skenario di atas ada test-nya dan hijau
- Unknown ingredient **tidak** menghasilkan error — ini verifikasi Delta 2
- Semua response error mengikuti format §A.10.5
- Test pakai `TestClient`, dataset nyata

**Done:** `uv run pytest tests/integration/test_recommendations_validation.py -v`

---

### T-P4-10 · Integration test — Contract Delta v1.1

```text
Fase     : 4
Depends  : T-P4-09
File     : —
Test     : apps/api/tests/integration/test_contract_delta.py
```

**Deskripsi:** Test khusus yang memverifikasi ketiga Delta v1.1 di level HTTP. Dipisah
agar delta ini tidak diam-diam hilang saat refactor.

**Acceptance:**
- **Delta 1:** request dengan bahan utama lengkap tapi tanpa garam/minyak →
  `matchPercentage` 100, `missingIngredients` **tidak** memuat `salt`/`cooking_oil`.
  Field `ingredients` **tetap** memuat keduanya.
- **Delta 2:** request `["telur","kangkung"]` → 200, `unknownIngredients == ["kangkung"]`,
  `results` tetap berisi resep berbahan telur
- **Delta 2 (semua unknown):** `["kangkung","durian"]` → 200, `results: []`,
  `unknownIngredients` 2 item
- **Delta 3:** request `["telur","ayam"]` → `query.raw == ["telur","ayam"]`,
  `query.ingredients == ["egg","chicken"]`
- **Delta 3 (dedupe):** `["telur","telur","eggs"]` → `query.ingredients == ["egg"]`

**Done:** `uv run pytest tests/integration/test_contract_delta.py -v`

---

### T-P4-11 · Route GET /recipes/{id}

```text
Fase     : 4
Depends  : T-P4-06, T-P3-13
File     : apps/api/app/api/v1/routes/recipes.py
Test     : apps/api/tests/integration/test_recipes.py
```

**Deskripsi:** Endpoint detail resep §A.10.2.

**Acceptance:**
- `GET /api/v1/recipes/recipe_001` → 200, struktur sesuai §A.10.2
- `GET /api/v1/recipes/nonexistent` → 404 `RECIPE_NOT_FOUND`
- Response **tanpa** field match-related
- Route memanggil repository lewat dependency, bukan `open()` file
- `response_model` diset

**Done:** `uv run pytest tests/integration/test_recipes.py -v`

---

### T-P4-12 · Route GET /ingredients

```text
Fase     : 4
Depends  : T-P4-06, T-P3-13
File     : apps/api/app/api/v1/routes/ingredients.py
Test     : apps/api/tests/integration/test_ingredients.py
```

**Deskripsi:** Endpoint kamus bahan §A.10.3, untuk autocomplete & showcase.

**Acceptance:**
- `GET /api/v1/ingredients` → 200
- Mengembalikan ~120 ingredient dengan `name`, `displayName`, `aliases`, `category`,
  `staple`
- `meta.count` cocok dengan panjang array
- Urutan stabil antar request (determinisme)

**Done:** `uv run pytest tests/integration/test_ingredients.py -v`

---

### T-P4-13 · Health endpoint lengkap

```text
Fase     : 4
Depends  : T-P3-13, T-P1-07
File     : apps/api/app/api/v1/routes/health.py
Test     : apps/api/tests/integration/test_health.py
```

**Deskripsi:** Perluas health dari T-P1-07 menjadi §A.10.4 — memuat `recipeCount` dan
`ingredientCount` sebagai bukti dataset ter-load.

**Acceptance:**
- `GET /api/v1/health` → `{"status":"ok","recipeCount":60,"ingredientCount":<n>}`
- Angka berasal dari repository, bukan konstanta hardcode
- Tetap cepat — tidak me-reload dataset per request

**Done:** `uv run pytest tests/integration/test_health.py -v`

---

### T-P4-14 · Logging & request ID

```text
Fase     : 4
Depends  : T-P4-03
File     : apps/api/app/core/logging.py, apps/api/app/main.py
Test     : apps/api/tests/integration/test_logging.py
```

**Deskripsi:** Middleware logging sesuai `technical-architecture.md` §18.

Field wajib: `request_id`, `method`, `path`, `status_code`, `duration_ms`.
Untuk endpoint recommendations tambah: `ingredient_count`, `result_count`.

**Acceptance:**
- Setiap request menghasilkan satu log entry dengan 5 field wajib
- `request_id` unik per request, ikut di response header (`X-Request-ID`) agar bisa
  dikorelasikan
- Log recommendations memuat `ingredient_count` dan `result_count`
- **Tidak** melog: isi lengkap bahan user, secret, API key, header Authorization
  (technical-architecture §18, PRD §14)
- Log level dari `settings.log_level`
- Unhandled exception ter-log dengan stack trace (di server, bukan response)

**Done:** `uv run pytest tests/integration/test_logging.py -v`

---

### T-P4-15 · OpenAPI polish

```text
Fase     : 4
Depends  : T-P4-08, T-P4-11, T-P4-12, T-P4-13
File     : apps/api/app/main.py, semua route
```

**Deskripsi:** Lengkapi metadata OpenAPI agar `/docs` bisa dipakai reviewer tanpa
membaca kode (PRD FR-11).

**Acceptance:**
- `title`, `description`, `version` terisi bermakna
- Setiap endpoint punya `summary` dan `description`
- Setiap endpoint punya contoh request dan/atau response
- Response error terdokumentasi per endpoint (`responses={400:..., 404:...}`)
- Tag pengelompokan endpoint (`recommendations`, `recipes`, `ingredients`, `system`)
- `/docs` dan `/openapi.json` bisa diakses
- Contoh di OpenAPI **cocok** dengan response nyata — diverifikasi manual

**Done:** buka `/docs`, coba "Try it out" pada setiap endpoint.

---

### T-P4-16 · Benchmark latency

```text
Fase     : 4
Depends  : T-P4-08
File     : apps/api/scripts/benchmark_latency.py
```

**Deskripsi:** Ukur latency `POST /recommendations` terhadap target PRD §14:
p50 < 200ms, p95 < 500ms. Angka diukur, bukan diasumsikan
(`technical-architecture.md` §19).

**Acceptance:**
- Script menjalankan ≥100 request dengan input bervariasi
- Melaporkan p50, p95, p99, min, max
- p50 < 200ms dan p95 < 500ms pada environment lokal
- Ada warm-up sebelum pengukuran (request pertama memuat dataset)
- Hasil dicatat untuk dipakai di README (P6)

**Done:** `uv run python scripts/benchmark_latency.py` — verifikasi angka memenuhi target.

**Catatan:** kalau p95 gagal, periksa apakah dataset di-reload per request
(pelanggaran T-P3-13).

---
---

# PHASE 5 — FRONTEND

**Goal fase:** demo interaktif memakai API nyata, empat state eksplisit.
**Exit criteria:** `development-roadmap.md` §6.3.

**Aturan mutlak fase ini:** tidak ada business logic di component. Semua request lewat
`lib/api/`. Semua copy dari `lib/constants/content.ts`.

---

### T-P5-01 · Types dari kontrak API

```text
Fase     : 5
Depends  : T-P4-05, T-P1-08
File     : apps/web/types/api.ts
```

**Deskripsi:** TypeScript type yang mencerminkan kontrak `content-schema.md` §A.10 —
termasuk Delta v1.1.

Type: `RecommendationRequest`, `RecommendationResponse`, `Query`, `Recommendation`,
`Meta`, `Recipe`, `Ingredient`, `ApiError`, `Difficulty`, `IngredientCategory`.

**Acceptance:**
- Field `camelCase` sesuai response API
- `query.raw` dan `query.ingredients` ada (Delta 3)
- `unknownIngredients: string[]` ada di root response (Delta 2)
- `Difficulty` sebagai union `'easy' | 'medium' | 'hard'`, bukan `string`
- `ApiError` mencerminkan `{error: {code, message, details}}`
- Error code sebagai union type — agar mapping di T-P5-04 exhaustive
- Tidak ada `any`
- `pnpm typecheck` lewat

**Done:** `pnpm typecheck`

---

### T-P5-02 · Content constants

```text
Fase     : 5
Depends  : T-P1-08
File     : apps/web/lib/constants/content.ts
```

**Deskripsi:** Seluruh copy dari `content-schema.md` Bagian B, terpusat di satu file
(§B.12) — bukan string literal tersebar di JSX.

Cakupan: hero (§B.2), input (§B.3), chip (§B.4), state rekomendasi (§B.5), card (§B.6),
detail (§B.7), error mapping (§B.8), validasi (§B.9), showcase (§B.10), meta (§B.11).

**Acceptance:**
- Semua key di `content-schema.md` Bagian B ada
- Placeholder pakai format `{count}`, `{percentage}`, dst. (§B.12)
- Objek `as const` agar key ter-typecheck
- Label `difficulty` dan tier `matchPercentage` (§B.6.1, §B.6.2) termasuk
- Tidak ada emoji
- Bahasa Indonesia, sapaan `kamu` (§B.1)

**Done:** `pnpm typecheck`

---

### T-P5-03 · UI primitives

```text
Fase     : 5
Depends  : T-P1-09
File     : apps/web/components/ui/
Test     : apps/web/tests/components/ui.test.tsx
```

**Deskripsi:** Component generik: `Button`, `Input`, `Badge`, `Card`, `Skeleton`,
`Alert`, `Spinner` (`component-architecture.md` §9).

**Acceptance:**
- Semua component generik — **tidak** tahu soal resep/bahan
- Tidak ada `RecipeCard` atau logic domain di folder `ui/`
  (`component-architecture.md` §9 larangan eksplisit)
- `Button` punya state `disabled` dan `loading`
- `Input` menerima `id`/`aria-label` untuk aksesibilitas
- Fokus terlihat (focus ring) — tidak dihapus
- Props ter-type, tanpa `any`
- Test render dasar hijau

**Done:** `pnpm test && pnpm typecheck`

---

### T-P5-04 · API client + error mapping

```text
Fase     : 5
Depends  : T-P5-01, T-P5-02
File     : apps/web/lib/api/client.ts, recommendations.ts, recipes.ts, ingredients.ts
Test     : apps/web/tests/lib/api.test.ts
```

**Deskripsi:** Satu layer HTTP (`component-architecture.md` §11). Base URL dari
`NEXT_PUBLIC_API_BASE_URL`. Mapping `error.code` → pesan user sesuai §B.8.

**Acceptance:**
- Base URL dari env, **tidak** hardcode `localhost`
- Component tidak pernah menyusun URL sendiri — semua lewat modul ini
- Error API di-parse menjadi objek bertipe dengan `code`
- Mapping code → pesan pakai `content.ts` (§B.8), bukan `error.message` mentah dari API
- Network failure / timeout ditangani terpisah dari error HTTP (§B.8 baris network)
- Unknown error code → pesan fallback
- Ada timeout request (jangan menggantung tanpa batas)
- Test dengan mock fetch: sukses, 400, 404, 422, 500, network error

**Done:** `pnpm test`

---

### T-P5-05 · Hook useRecommendations

```text
Fase     : 5
Depends  : T-P5-04
File     : apps/web/hooks/useRecommendations.ts
Test     : apps/web/tests/hooks/useRecommendations.test.tsx
```

**Deskripsi:** State management request rekomendasi (`component-architecture.md` §12):
`idle` | `loading` | `success` | `error`.

Mengembalikan: `status`, `data`, `errorMessage`, `submit(ingredients)`, `reset()`.

**Acceptance:**
- Empat status eksplisit — bukan kombinasi boolean `isLoading`/`isError` yang bisa
  inkonsisten
- `data` memuat `results`, `query`, `unknownIngredients` (Delta 2 & 3 sampai ke UI)
- Request berurutan: hasil request lama tidak menimpa request baru (race condition)
- Tidak ada business logic — tidak menghitung, tidak menormalisasi, tidak me-sort
- Hook tidak memanggil `fetch` langsung — lewat `lib/api/`
- Test: transisi state sukses, error, dan reset

**Done:** `pnpm test`

---

### T-P5-06 · IngredientInput

```text
Fase     : 5
Depends  : T-P5-03, T-P5-02
File     : apps/web/components/ingredients/IngredientInput.tsx
Test     : apps/web/tests/components/IngredientInput.test.tsx
```

**Deskripsi:** Input bahan comma-separated (`component-architecture.md` §6).
Submit via tombol dan Enter. Validasi UI ringan §B.9.

**Acceptance:**
- Comma-separated diterima
- Submit via tombol **dan** Enter
- Validasi §B.9: kosong / >30 bahan / nama >60 karakter → blok submit + pesan
- Pesan validasi dari `content.ts`
- Tombol contoh input (§B.3 `input.examples`) mengisi field
- Component **tidak** melakukan normalisasi canonical — itu server
- Component **tidak** memanggil API langsung; hanya `onSubmit(ingredients)`
  (`component-architecture.md` §6)
- Label terhubung ke input (`htmlFor`/`id`)
- Pesan error terhubung via `aria-describedby`
- Bisa dioperasikan penuh dengan keyboard
- Test: render, ketik, submit tombol, submit Enter, validasi kosong

**Done:** `pnpm test`

---

### T-P5-07 · IngredientTag (chip normalisasi — Delta 2 & 3)

```text
Fase     : 5
Depends  : T-P5-03, T-P5-02
File     : apps/web/components/ingredients/IngredientTag.tsx
Test     : apps/web/tests/components/IngredientTag.test.tsx
```

**Deskripsi:** Chip yang menampilkan hasil normalisasi §B.4 — implementasi UI untuk
Delta 3, dan penanda unknown untuk Delta 2.

Tiga varian: `normalized` (`telur → Telur`), `plain` (`Telur`), `unknown`
(`kangkung · tidak dikenali`).

**Acceptance:**
- Varian `normalized` menampilkan mapping input → displayName (Delta 3)
- Varian `unknown` menampilkan suffix "tidak dikenali" (Delta 2) dengan gaya visual
  berbeda
- Tooltip dari `content.ts` (§B.4)
- Tooltip tidak hanya `title` attribute — informasi penting juga tersedia sebagai teks
  yang terbaca screen reader
- Perbedaan varian tidak **hanya** lewat warna (aksesibilitas)
- Test: tiga varian render benar

**Done:** `pnpm test`

---

### T-P5-08 · MatchBadge

```text
Fase     : 5
Depends  : T-P5-03, T-P5-02
File     : apps/web/components/recommendations/MatchBadge.tsx
Test     : apps/web/tests/components/MatchBadge.test.tsx
```

**Deskripsi:** Badge persentase kecocokan dengan tier visual §B.6.2.

**Acceptance:**
- `100` → tier `perfect`; `70–99` → `high`; `50–69` → `medium`; `30–49` → `low`
- Label tier dari `content.ts` (§B.6.2)
- Teks `{percentage}% cocok` — integer tanpa desimal (§B.13)
- Tier ditentukan oleh fungsi murni yang bisa diuji, bukan ternary bertumpuk di JSX
- Kontras warna memadai untuk semua tier
- Informasi tier tidak hanya lewat warna — ada teks
- Test: batas tier (30, 49, 50, 69, 70, 99, 100)

**Done:** `pnpm test`

---

### T-P5-09 · RecommendationCard

```text
Fase     : 5
Depends  : T-P5-08, T-P5-01
File     : apps/web/components/recommendations/RecommendationCard.tsx
Test     : apps/web/tests/components/RecommendationCard.test.tsx
```

**Deskripsi:** Kartu rekomendasi sesuai layout `component-architecture.md` §7 dan copy
§B.6.

**Acceptance:**
- Menampilkan: nama, `MatchBadge`, available, missing, waktu, difficulty, porsi, CTA
- `missingIngredients` kosong → tampilkan `card.missingEmpty`, bukan list kosong
- Label difficulty diterjemahkan via §B.6.1 (`easy` → `Mudah`)
- Format angka sesuai §B.13
- **Tidak menghitung apa pun** — semua nilai dari props
- CTA menuju halaman detail resep
- Struktur heading semantik (nama resep sebagai heading, bukan `div`)
- Available/missing dibedakan tidak hanya lewat ikon warna — ada label teks
- Test: render lengkap, kasus missing kosong, label difficulty

**Done:** `pnpm test`

---

### T-P5-10 · State components

```text
Fase     : 5
Depends  : T-P5-03, T-P5-02
File     : apps/web/components/recommendations/RecommendationSkeleton.tsx, RecommendationEmpty.tsx, RecommendationError.tsx
Test     : apps/web/tests/components/RecommendationStates.test.tsx
```

**Deskripsi:** Component terpisah per state (`component-architecture.md` §30) — bukan
conditional bertumpuk dalam satu component besar.

**Acceptance:**
- `RecommendationSkeleton` menampilkan 3 placeholder card
- `RecommendationEmpty` pakai copy §B.5.4 + CTA
- `RecommendationEmpty` punya **varian khusus** "semua bahan tidak dikenali" §B.5.5
  yang menyebut daftar bahan yang tidak dikenali (Delta 2)
- `RecommendationError` pakai copy §B.5.6 + tombol retry yang berfungsi
- Semua copy dari `content.ts`
- Skeleton tidak diumumkan berulang ke screen reader (`aria-busy`/`aria-hidden` tepat)
- Test: masing-masing state render benar; varian all-unknown menampilkan daftar bahan

**Done:** `pnpm test`

---

### T-P5-11 · RecommendationList & Section

```text
Fase     : 5
Depends  : T-P5-09, T-P5-10, T-P5-05
File     : apps/web/components/recommendations/RecommendationList.tsx, RecommendationSection.tsx
Test     : apps/web/tests/components/RecommendationList.test.tsx
```

**Deskripsi:** `RecommendationList` merender array (`component-architecture.md` §7).
`RecommendationSection` memilih state mana yang tampil berdasarkan `status` dari hook.

**Acceptance:**
- `RecommendationList` **tidak** menghitung match percentage, tidak me-sort ulang —
  urutan dari API dipertahankan
- `RecommendationSection` memetakan `status` → component state (idle/loading/success/
  empty/error) dengan pemetaan eksplisit
- Kasus `success` tapi `results` kosong → `RecommendationEmpty`
- Kasus `results` kosong **dan** semua input unknown → varian §B.5.5
- Heading jumlah hasil §B.5.3, bentuk tunggal ditangani (`headingSingle`)
- Hasil diumumkan ke screen reader (`aria-live="polite"`)
- Chip normalisasi (T-P5-07) ditampilkan di section ini dari `query` +
  `unknownIngredients`
- Test: tiap status merender component yang benar

**Done:** `pnpm test`

---

### T-P5-12 · RecipeDetail components

```text
Fase     : 5
Depends  : T-P5-03, T-P5-01
File     : apps/web/components/recipes/RecipeDetail.tsx, RecipeHeader.tsx, RecipeIngredientList.tsx, RecipeInstructionList.tsx, RecipeMeta.tsx
Test     : apps/web/tests/components/RecipeDetail.test.tsx
```

**Deskripsi:** Detail resep (`component-architecture.md` §8) dengan copy §B.7.

**Acceptance:**
- Menampilkan nama, deskripsi, bahan lengkap, langkah, waktu, difficulty, porsi
- Bahan `required: false` diberi suffix `(opsional)` (§B.7)
- `detail.stapleNote` ditampilkan — menjelaskan kenapa garam/minyak tidak dihitung
  (transparansi Delta 1)
- Langkah dirender sebagai `<ol>` — nomor dari markup, bukan dari string
- Bahan dirender sebagai `<ul>`
- Component tidak memanggil API sendiri (data dari page)
- Test: render lengkap, suffix opsional, staple note tampil

**Done:** `pnpm test`

---

### T-P5-13 · Halaman detail resep

```text
Fase     : 5
Depends  : T-P5-12, T-P5-04
File     : apps/web/app/recipes/[id]/page.tsx
Test     : apps/web/tests/pages/recipeDetail.test.tsx
```

**Deskripsi:** Route dinamis yang mengambil resep via API client dan merender
`RecipeDetail`.

**Acceptance:**
- `/recipes/recipe_001` menampilkan detail
- Id tidak ada → tampilkan not-found dengan copy §B.7 (`detail.notFound`)
- Ada tombol "Kembali ke hasil" (§B.7)
- Loading state ditangani
- Data diambil lewat `lib/api/recipes.ts`, bukan `fetch` langsung di page
- Metadata halaman (title) memuat nama resep

**Done:** `pnpm test && pnpm build`

---

### T-P5-14 · HeroSection & Footer

```text
Fase     : 5
Depends  : T-P5-02, T-P5-03
File     : apps/web/components/HeroSection.tsx, apps/web/components/Footer.tsx
Test     : apps/web/tests/components/Hero.test.tsx
```

**Deskripsi:** Hero §B.2 dan footer §B.11.

**Acceptance:**
- Judul hero: "Apa yang bisa saya masak dari bahan yang sudah ada?" (PRD §8.6)
- Subtitle dan badge dari `content.ts`
- Footer memuat tagline + link repo
- Satu `<h1>` per halaman
- Test render hijau

**Done:** `pnpm test`

---

### T-P5-15 · Komposisi halaman utama

```text
Fase     : 5
Depends  : T-P5-06, T-P5-11, T-P5-14
File     : apps/web/app/page.tsx, apps/web/app/layout.tsx
Test     : apps/web/tests/pages/home.test.tsx
```

**Deskripsi:** Menyusun halaman utama sesuai `component-architecture.md` §5.1.
Page hanya komposisi + state wiring — **tanpa** algoritma.

**Acceptance:**
- Struktur: `HeroSection` → `IngredientInput` → `RecommendationSection` → (showcase P6)
  → `Footer`
- Page menghubungkan `onSubmit` dari input ke `submit` dari hook
- Page **tidak** memanggil `fetch`, tidak menghitung, tidak menormalisasi
- Metadata §B.11 diset di layout
- Bukan god-component (`component-architecture.md` §34)
- `pnpm build` sukses

**Done:** `pnpm test && pnpm build`

---

### T-P5-16 · Integrasi end-to-end manual dengan API nyata

```text
Fase     : 5
Depends  : T-P5-15, T-P4-08
File     : apps/web/.env.example
```

**Deskripsi:** Verifikasi frontend berbicara dengan API nyata (PRD FR-10), bukan mock.

**Acceptance:**
- `NEXT_PUBLIC_API_BASE_URL` terdokumentasi di `.env.example`
- API jalan di `:8000`, web di `:3000`, request berhasil tanpa error CORS
- Input `telur, ayam, wortel` → kartu resep nyata muncul
- Chip normalisasi menampilkan `telur → Telur` (Delta 3)
- Input `telur, kangkung` → chip "tidak dikenali" muncul, hasil tetap ada (Delta 2)
- Klik kartu → halaman detail terbuka dengan data benar
- Matikan API → error state tampil dengan pesan network (§B.8), bukan crash
- Tidak ada mock/data hardcode yang tertinggal di kode

**Done:** jalankan kedua server, lalui semua skenario di atas.

---

### T-P5-17 · Audit copy & konstanta

```text
Fase     : 5
Depends  : T-P5-15
File     : apps/web/
```

**Deskripsi:** Verifikasi tidak ada copy yang tertinggal sebagai string literal di JSX
(`content-schema.md` §B.12, exit criteria `development-roadmap.md` §6.3).

**Acceptance:**
- Grep string berbahasa Indonesia di `components/`, `app/`, `hooks/` → tidak ada
  (kecuali import dari `content.ts`)
- Tidak ada URL API hardcode di luar `lib/api/`
- Tidak ada angka magic untuk threshold/limit di frontend — nilai berasal dari
  `meta` response atau konstanta bernama
- Placeholder terinterpolasi benar (tidak ada `{count}` bocor ke layar)

**Done:** `grep -rn "[a-z] \(yang\|kamu\|bahan\|resep\)" apps/web/components apps/web/app`
— hasil hanya dari `content.ts`.

---

### T-P5-18 · Audit aksesibilitas

```text
Fase     : 5
Depends  : T-P5-15
File     : apps/web/
```

**Deskripsi:** Verifikasi exit criteria aksesibilitas `development-roadmap.md` §6.3.

**Acceptance:**
- Seluruh alur (input → submit → hasil → detail → kembali) bisa dilalui **hanya dengan
  keyboard**
- Fokus terlihat di semua elemen interaktif
- Input punya label terasosiasi
- Hasil diumumkan via `aria-live`
- Loading state tidak membingungkan screen reader
- Tidak ada informasi yang **hanya** disampaikan lewat warna (tier match, available/
  missing, unknown)
- Kontras teks memadai
- Gambar/ikon dekoratif `aria-hidden`, yang bermakna punya label
- Struktur heading hierarkis (satu `h1`, tidak melompat level)

**Done:** navigasi keyboard manual + inspeksi DOM untuk atribut ARIA.

---

### T-P5-19 · Verifikasi contoh input

```text
Fase     : 5
Depends  : T-P5-16, T-P2-08
File     : apps/web/lib/constants/content.ts
```

**Deskripsi:** Contoh input di §B.3 harus benar-benar menghasilkan hasil bagus pada
dataset final — kalau contoh menghasilkan 0 resep, demo langsung terlihat rusak.

**Acceptance:**
- `telur, ayam, wortel` → ≥3 resep
- `tahu, tempe, kecap` → ≥3 resep
- `nasi, telur, bawang putih` → ≥3 resep
- Setiap contoh menghasilkan sebaran match% (ada yang tinggi, ada yang sedang)
- Bila ada contoh yang gagal: ganti contohnya **atau** perbaiki dataset — jangan
  dibiarkan

**Done:** uji ketiga contoh lewat UI, catat jumlah hasil.

---
---

# PHASE 6 — PORTFOLIO & DEPLOY

**Goal fase:** reviewer paham produk, arsitektur, dan trade-off tanpa membaca kode; demo
live bisa dicoba.
**Exit criteria:** `development-roadmap.md` §7.3.

---

### T-P6-01 · Showcase — RequestExample & ResponseExample

```text
Fase     : 6
Depends  : T-P5-15, T-P4-15
File     : apps/web/components/showcase/RequestExample.tsx, ResponseExample.tsx
Test     : apps/web/tests/components/showcase.test.tsx
```

**Deskripsi:** Tampilkan contoh request/response §B.10.1, §B.10.2 dengan tombol copy.

**Acceptance:**
- Contoh request format HTTP + JSON body
- Contoh response JSON terformat, mudah dibaca
- Tombol copy berfungsi, label berubah ke "Tersalin" (§B.10)
- Contoh **cocok** dengan response API nyata — diverifikasi dengan membandingkan
  langsung
- Contoh diambil dari satu sumber (konstanta/fixture), bukan ditulis ulang di dua tempat
  (mitigasi contract drift, §B.10.2)
- Tombol copy punya label aksesibel

**Done:** `pnpm test`, lalu bandingkan contoh dengan output `curl` nyata.

---

### T-P6-02 · Showcase — ArchitectureDiagram & TechStack

```text
Fase     : 6
Depends  : T-P5-15
File     : apps/web/components/showcase/ArchitectureDiagram.tsx, TechStack.tsx
```

**Deskripsi:** Diagram alur §B.10.3 dan daftar tech stack §B.10.4.

**Acceptance:**
- Diagram menunjukkan alur Browser → Next.js → API → Normalizer → Engine → Ranking →
  Repository → JSON
- Diagram terbaca di layar kecil (responsif), bukan ASCII yang pecah di mobile
- Tech stack dikelompokkan per layer §B.10.4
- Diagram punya alternatif teks untuk screen reader

**Done:** `pnpm build`, verifikasi visual di viewport mobile & desktop.

---

### T-P6-03 · Showcase — catatan keputusan teknis

```text
Fase     : 6
Depends  : T-P5-02
File     : apps/web/components/showcase/TechnicalDecisions.tsx
```

**Deskripsi:** Tiga catatan keputusan §B.10.5 — bagian yang menunjukkan reasoning
produk, bukan hanya hasil.

**Acceptance:**
- Tiga kartu: kenapa deterministik, kenapa staple dikecualikan, kenapa JSON
- Copy dari `content.ts` §B.10.5
- Setiap catatan menyebut **trade-off**, bukan hanya keunggulan
- Terbaca dalam ≤30 detik per kartu

**Done:** `pnpm build`, review isi.

---

### T-P6-04 · Komposisi ApiShowcase di halaman utama

```text
Fase     : 6
Depends  : T-P6-01, T-P6-02, T-P6-03
File     : apps/web/components/showcase/ApiShowcase.tsx, apps/web/app/page.tsx
```

**Deskripsi:** Gabungkan komponen showcase dan sisipkan ke halaman utama di bawah hasil
rekomendasi (`component-architecture.md` §5.1).

**Acceptance:**
- Showcase muncul di halaman utama, **di bawah** area fungsional — tidak mengganggu alur
  utama (PRD §5 fokus satu journey)
- Heading §B.10 (`showcase.heading`, `showcase.subheading`)
- Link ke `/docs` OpenAPI berfungsi
- `pnpm build` sukses

**Done:** `pnpm build`, verifikasi visual halaman utama.

---

### T-P6-05 · README

```text
Fase     : 6
Depends  : T-P5-16, T-P4-16
File     : README.md
```

**Deskripsi:** Dokumen utama yang dibaca reviewer pertama kali.

Struktur wajib:
1. Judul + satu paragraf: masalah & solusi
2. Demo link + screenshot/GIF
3. Cara kerja recommendation engine (formula + contoh 3/4 → 75%)
4. Arsitektur (diagram + penjelasan layer)
5. Cara menjalankan lokal — langkah lengkap dari clone
6. Contoh API (request + response nyata)
7. Testing (perintah + cakupan)
8. Keputusan teknis & trade-off
9. Roadmap / apa yang belum dikerjakan dan alasannya

**Acceptance:**
- Semua 9 bagian ada
- Setup instructions **lengkap**: prasyarat (Python 3.12, Node, uv, pnpm), langkah
  API, langkah web, env var
- Contoh request/response **nyata** (hasil `curl`), bukan karangan
- Angka latency dari T-P4-16 dicantumkan sebagai hasil ukur
- Menyebut Contract Delta v1.1 (staple exclusion, unknownIngredients) sebagai keputusan
  produk
- Bagian "belum dikerjakan" jujur menyebut AI phase & kuantitas bahan sebagai future
- Tidak ada secret/API key
- Tidak ada placeholder `TODO` yang tertinggal

**Done:** baca ulang seperti reviewer yang belum pernah lihat proyek ini.

---

### T-P6-06 · Verifikasi setup dari clone bersih

```text
Fase     : 6
Depends  : T-P6-05
File     : README.md
```

**Deskripsi:** Uji instruksi README dengan clone repo ke direktori baru dan mengikuti
langkahnya **apa adanya** — tanpa memakai environment yang sudah ter-setup.

**Acceptance:**
- Clone ke direktori kosong, ikuti README langkah demi langkah
- API jalan, web jalan, rekomendasi keluar
- Tidak ada langkah yang tersirat/hilang (mis. `cp .env.example .env` yang lupa ditulis)
- Setiap perintah di README benar-benar berjalan seperti tertulis
- Bila ada langkah yang gagal: **perbaiki README**, bukan cari jalan pintas manual

**Done:** proses clone-to-running selesai tanpa improvisasi.

---

### T-P6-07 · Studi kasus produk

```text
Fase     : 6
Depends  : T-P6-05
File     : docs/case-study.md
```

**Deskripsi:** Narasi product management sesuai PRD §25 — bagian yang membedakan proyek
ini dari sekadar coding exercise.

Struktur: masalah → insight → keputusan scope → trade-off → hasil → apa yang akan
dilakukan berbeda.

**Acceptance:**
- Menjelaskan **kenapa scope MVP dipilih** (kenapa bukan AI dulu, kenapa bukan gambar
  dulu)
- Menjelaskan keputusan staple exclusion sebagai contoh keputusan produk yang berasal
  dari pertanyaan terbuka (PRD §26 Q1)
- Menyebut trade-off yang diambil, bukan hanya keberhasilan
- Menyebut metrik yang dipakai untuk menilai keberhasilan (PRD §17)
- Bahasa produk, bukan bahasa implementasi

**Done:** review isi — apakah pembaca non-teknis paham keputusannya?

---

### T-P6-08 · Screenshot & GIF demo

```text
Fase     : 6
Depends  : T-P5-16
File     : docs/assets/
```

**Deskripsi:** Bukti visual alur utama untuk README.

**Acceptance:**
- Screenshot: halaman awal, hasil rekomendasi, detail resep, empty state, API showcase
- GIF alur utama: input → hasil → detail
- Ukuran file wajar (GIF dikompres, tidak puluhan MB)
- Ter-embed di README dan tampil benar di GitHub
- Tidak ada informasi pribadi di screenshot

**Done:** buka README di GitHub, verifikasi semua aset tampil.

---

### T-P6-09 · Dockerfile API & web

```text
Fase     : 6
Depends  : T-P4-15, T-P5-15
File     : docker/api.Dockerfile, docker/web.Dockerfile
```

**Deskripsi:** Container image untuk kedua app.

Cek praktik terbaru Dockerfile untuk `uv` dan Next.js standalone output lewat
`context7` — pola build berubah antar versi.

**Acceptance:**
- Multi-stage build (dependency layer terpisah dari source)
- Base image versi ter-pin (bukan `latest`)
- Jalan sebagai **non-root user**
- Dataset `data/recipes/` tersedia di image API
- `.dockerignore` mengecualikan `.venv`, `node_modules`, `.git`, `.env`
- **Tidak ada secret** di image layer maupun build arg
- Image API start dan `/api/v1/health` merespons
- Image web start dan halaman render

**Done:** build kedua image, jalankan, cek health & halaman.

---

### T-P6-10 · docker-compose

```text
Fase     : 6
Depends  : T-P6-09
File     : docker-compose.yml
```

**Deskripsi:** Orchestration lokal dua service (`technical-architecture.md` §23).
Tanpa database — belum dibutuhkan.

**Acceptance:**
- Service `api` (port 8000) dan `web` (port 3000)
- `web` menerima `NEXT_PUBLIC_API_BASE_URL` yang menunjuk `api`
- `api` menerima `CORS_ORIGINS` yang mengizinkan origin `web`
- Healthcheck pada service `api`
- `web` depends_on `api`
- **Tidak ada** service yang tidak dibutuhkan (redis, postgres) — §23 larangan eksplisit
- Env dari `.env`, tidak ada secret ter-hardcode di compose file
- `docker compose up` → alur end-to-end berfungsi di browser

**Done:** `docker compose up`, buka `localhost:3000`, cari resep.

---

### T-P6-11 · E2E Playwright

```text
Fase     : 6
Depends  : T-P5-16
File     : apps/web/e2e/, apps/web/playwright.config.ts
Test     : apps/web/e2e/recommendations.spec.ts
```

**Deskripsi:** E2E alur utama sesuai `technical-architecture.md` §20.4.

Skenario: buka situs → input bahan → klik cari → hasil muncul → buka detail.

Cek konfigurasi Playwright terbaru (`webServer`, locator API) lewat `context7`.

**Acceptance:**
- Alur utama hijau terhadap API nyata (bukan mock)
- Skenario tambahan: bahan tidak dikenali → chip unknown muncul, hasil tetap ada (Delta 2)
- Skenario: input kosong → validasi tampil, tidak ada request terkirim
- Locator pakai role/label (aksesibel), bukan selector CSS rapuh
- `webServer` terkonfigurasi agar test bisa jalan mandiri
- Tidak flaky — jalan 3x berturut hijau

**Done:** `pnpm exec playwright test` — jalankan 3x.

---

### T-P6-12 · CI lengkap + E2E

```text
Fase     : 6
Depends  : T-P6-11, T-P1-11
File     : .github/workflows/ci.yml
```

**Deskripsi:** Perluas CI dengan job E2E dan coverage gate.

**Acceptance:**
- Job `api`: ruff + pytest + coverage gate (≥90% domain/services)
- Job `web`: lint + typecheck + test + build
- Job `e2e`: start API + web, jalankan Playwright
- Job `dataset`: jalankan `validate_dataset.py` — dataset rusak = CI merah
- Test boundary arsitektur (T-P3-11) ikut jalan
- Semua job hijau
- Artefak Playwright (trace/screenshot) diunggah saat gagal

**Done:** push, `gh run list` menunjukkan semua job sukses.

---

### T-P6-13 · Deploy web & API

```text
Fase     : 6
Depends  : T-P6-10, T-P6-12
File     : (konfigurasi platform)
```

**Deskripsi:** Deploy web ke Vercel, API ke platform container/server
(`technical-architecture.md` §25).

Langkah berurutan — penting agar CORS tidak salah konfigurasi:

1. Deploy API lebih dulu, catat URL production-nya.
2. Set `CORS_ORIGINS` di API ke domain web production (setelah langkah 4, perbarui bila
   domain berubah).
3. Deploy web dengan `NEXT_PUBLIC_API_BASE_URL` menunjuk URL API dari langkah 1.
4. Uji end-to-end di production.
5. Perbarui link demo di README.

**Acceptance:**
- API ter-deploy, `/api/v1/health` merespons dengan `recipeCount: 60`
- Web ter-deploy, alur input → hasil → detail berfungsi
- HTTPS aktif di kedua sisi
- `CORS_ORIGINS` berisi domain web production saja — **bukan** `*`
- Tidak ada secret di repo maupun di bundle client (hanya `NEXT_PUBLIC_*` yang ke client)
- `.env` tidak ikut ter-deploy
- Link demo di README menunjuk deployment yang hidup
- E2E hijau terhadap production atau environment yang setara

**Done:** buka URL demo, lalui alur lengkap, cek `curl <api>/api/v1/health`.

**Catatan keamanan:** ini fase yang menyentuh environment publik. Verifikasi CORS dan
kebocoran secret **sebelum** mengumumkan link demo, bukan sesudah.

---
---

# PENUTUP

## Ringkasan Dependency Kritis

Task yang kalau salah akan merusak banyak task setelahnya:

| Task | Kenapa kritis |
|---|---|
| `T-P2-03` Validator | Gate seluruh kualitas dataset. Dibuat sebelum dataset, bukan sesudah. |
| `T-P2-09` Repository interface | Menentukan apakah migrasi ke PostgreSQL kelak murah atau mahal |
| `T-P3-05`/`T-P3-06` Scoring & engine | Inti nilai produk. Delta 1 hidup di sini. |
| `T-P3-13` Composition root | Salah di sini → dataset di-reload per request → target latency gagal |
| `T-P4-01` Base schema | Menentukan konsistensi `camelCase` seluruh API |
| `T-P4-07` Mapper | Satu-satunya tempat domain bertemu Pydantic |
| `T-P5-04` API client | Satu-satunya jalur frontend ke API |

## Titik Verifikasi Delta v1.1

Contract Delta v1.1 (`content-schema.md` §A.9) diuji di beberapa lapisan agar tidak
hilang saat refactor:

| Delta | Diuji di |
|---|---|
| 1 — Staple exclusion | `T-P3-05`, `T-P3-06` (unit), `T-P4-10` (integration), `T-P5-12` (UI note) |
| 2 — `unknownIngredients[]` | `T-P3-04` (unit), `T-P4-09`, `T-P4-10` (integration), `T-P5-07`, `T-P5-10` (UI), `T-P6-11` (E2E) |
| 3 — Normalisasi transparan | `T-P3-04` (unit), `T-P4-10` (integration), `T-P5-07` (UI) |

## Task yang Butuh Interaksi User

Agent tidak bisa menyelesaikan ini sendiri:

| Task | Butuh |
|---|---|
| `T-P1-12` | `gh auth login` interaktif, keputusan push |
| `T-P2-05`–`T-P2-08` | Review kelayakan kuliner resep |
| `T-P3-10` | Penilaian manual relevansi ranking |
| `T-P6-07` | Narasi produk — sudut pandang penulis |
| `T-P6-08` | Pengambilan screenshot |
| `T-P6-13` | Kredensial platform deploy |

## Aturan Commit

Satu task = satu commit (`AGENTS.md` §7). Sebut task ID:

```text
feat(matching): scoring function dengan staple exclusion (T-P3-05)
test(api): integration test contract delta v1.1 (T-P4-10)
feat(data): recipes batch 1 — 15 resep (T-P2-05)
docs: README dengan setup instructions (T-P6-05)
```

Push manual. Agent melaporkan "commit siap di-push", tidak push sendiri.

