# AGENTS.md — Smart Living API

Baca dokumen ini SEBELUM mengerjakan apapun di repository ini. Dokumen ini adalah
operating manual untuk AI agent (OpenCode / subagent) dan developer yang mengerjakan
proyek Smart Living API.

---

## 1. Tentang Proyek

Smart Living API adalah platform Smart Living berbasis API + frontend demo interaktif.
Inti nilai produk: mengubah bahan makanan sisa menjadi keputusan memasak yang berguna
melalui recommendation engine deterministik.

- **Posisi portfolio:** Product Manager + Backend/API Developer + Full-stack Developer.
- **Cakupan saat ini:** MVP (manual ingredient input → normalisasi → matching deterministik
  → ranking → REST API → frontend demo). AI adalah future phase, BUKAN bagian MVP.
- **Source of truth (urutan prioritas saat ada konflik):**

  ```
  PRD (WHAT & WHY)
    → technical-architecture (HOW)
    → component-architecture (WHERE & RESPONSIBILITY)
    → content-schema (DATA & CONTRACT)
    → implementation-task-breakdown (EXECUTION ORDER)
  ```

---

## 2. Urutan Baca Wajib (sebelum implementasi)

1. `docs/prd.md`
2. `docs/technical-architecture.md`
3. `docs/component-architecture.md`
4. `docs/content-schema.md`
5. `docs/development-roadmap.md`
6. `docs/implementation-task-breakdown.md`

Jangan mulai menulis kode sebelum memahami keempat dokumen di atas.

---

## 3. Keputusan Teknologi (terkunci)

| Area | Teknologi |
|---|---|
| Frontend | Next.js + TypeScript + Tailwind CSS |
| Backend | Python 3.12 + FastAPI + Pydantic v2 |
| Validation | Pydantic |
| Data MVP | JSON version-controlled (`data/recipes/`) |
| DB masa depan | PostgreSQL |
| API Docs | OpenAPI / Swagger (FastAPI auto) |
| Testing Backend | pytest + ruff |
| Testing Frontend | Vitest + React Testing Library |
| E2E | Playwright |
| Package/Runtime | `uv` (API), `pnpm` (web) |
| AI (future) | OpenAI API di balik service boundary |
| Container | Docker + docker-compose |
| CI | GitHub Actions |
| Deploy | Vercel (web) + container/server (API) |

> Node.js + Fastify tetap dianggap valid secara arsitektur, tapi baseline implementasi
> adalah FastAPI + Python (sesuai technical-architecture §3).

---

## 4. Aturan Dependency (HARD — dilarang dilanggar)

Diambil dari component-architecture §24–25. Pelanggaran = harus diperbaiki sebelum commit.

- Domain model (`domain/models`, `domain/matching`) **TIDAK BOLEH** import `fastapi`,
  `pydantic`, `react`, `openai`, atau koneksi database.
- API route **TIDAK BOLEH** akses repository langsung atau hitung match percentage.
  Route hanya: HTTP request → schema validation → service call → HTTP response.
- Matching engine **TIDAK BOLEH** melakukan HTTP request atau memanggil LLM.
- Repository **TIDAK BOLEH** menentukan ranking recommendation.
- AI service **TIDAK BOLEH** menyimpan business decision utama (ranking).
- Frontend hanya berbicara ke API lewat API client layer (`lib/api/`) — tidak ada
  akses database / business logic di React component.
- Shared types mewakili contract, bukan implementasi internal.

---

## 5. Konvensi Penamaan

**Backend (Python)**
- Module: `snake_case.py` (contoh: `recommendation_service.py`)
- Class: `PascalCase`
- Function: `snake_case`
- Field response JSON: `camelCase` (pakai `alias_generator` + `populate_by_name`
  di Pydantic agar mapping ke snake_case internal otomatis)

**Frontend (TS/React)**
- Component: `PascalCase.tsx` (contoh: `RecipeCard.tsx`)
- Hook: `useCamelCase.ts` (contoh: `useRecommendations.ts`)
- Utility: `camelCase.ts`

---

## 6. Dokumentasi Library & Framework (context7)

**Gunakan `context7` tool SETIAP KALI** butuh dokumentasi library/framework/SDK/API/
CLI/cloud service — termasuk yang kamu rasa sudah tahu. Training data mungkin tidak
mencerminkan versi terbaru. Prioritaskan context7 di atas web search untuk library docs.

Cara kerja:
1. `context7_resolve_library_id` untuk dapatkan library ID (kecuali user sudah beri
   format `/org/project` atau `/org/project/version`).
2. `context7_query_docs` dengan query spesifik (satu konsep per query).
3. Verifikasi versi yang dipakai proyek (`pyproject.toml` / `package.json`) sebelum
   menerapkan contoh kode.
4. Jangan asumsikan API dari ingatan.

**Gunakan context7 untuk:** FastAPI, Pydantic v2, pytest, ruff, uv, Next.js,
Tailwind CSS, Vitest, React Testing Library, Playwright, SWR/fetch, OpenAPI.

**Tidak perlu context7 untuk:** refactor logic murni, perbaikan bug business logic
tanpa library baru, review kode, penulisan dokumen.

---

## 7. Git & GitHub Workflow

Repo: `smart-living-API`, visibility **public**, remote `origin`, branch utama `main`.

### Setup awal (sekali, sebelum task pertama)
```bash
brew install gh                 # jika belum terinstall
gh auth login                   # interaktif — butuh user di terminal
git init -b main                # sudah dilakukan
# .gitignore sudah disediakan di root
git add . && git commit -m "chore: initial project docs & structure"
gh repo create smart-living-API --public --source=. --remote=origin --push
```

### Ritme commit
- **Commit per task selesai** (satu task = satu unit kerja logis, lihat
  `implementation-task-breakdown.md`), BUKAN per file per langkah kecil.
- Format **conventional commits**:
  ```
  <type>(<scope>): <subject>
  ```
  - `type`: `feat` | `fix` | `test` | `docs` | `chore` | `refactor` | `style`
  - `scope`: area (matching, api, web, data, ci, dsb.)
  - Contoh: `feat(matching): scoring function 3/4 -> 75`,
    `docs(api): content-schema contract delta v1.1`, `test(web): recipe card render`
- Subject bahasa Indonesia atau Inggris, singkat, self-contained (sebut task ID bila ada).
- Sebelum commit: `git status` + `git diff`, pastikan tidak ada `.env`/secret/
  `node_modules`/`.venv` ikut ter-stage.

### Push
- **Push MANUAL** — agent TIDAK auto-push. Agent hanya `git add` + `git commit`,
  lalu lapor "commit siap di-push" atau tanya user.
- Jangan `git push --force`. Jangan commit secret/API key.

### Aturan
- Jangan ubah struktur folder luas tanpa kebutuhan (component-architecture §39).
- Setiap perubahan harus incremental, dengan test bila menyentuh logic.

---

## 8. Kontrak Data & Delta (PENTING)

Technical-architecture.md BELUM mencerminkan 3 keputusan produk berikut. Sumber resmi
untuk ketiganya ada di `docs/content-schema.md` § "Contract Delta v1.1". Ikuti delta ini
saat implementasi:

1. **Staples dikecualikan scoring** — ingredient dengan `staple: true` (garam, minyak,
   air, lada, gula) tidak masuk `missingIngredients` dan tidak masuk denominator
   `matchPercentage`.
2. **`unknownIngredients[]` di response** — `POST /api/v1/recommendations` mengembalikan
   daftar bahan tak dikenali (di luar kamus) dengan HTTP 200, bukan error. Frontend
   menampilkan chip "tidak dikenali".
3. **Normalisasi transparan** — response membawa hasil normalisasi (`query.ingredients`
   canonical) agar frontend bisa tampilkan mapping `telur → egg`.

---

## 9. Aturan Data

- Jangan mengarang resep di luar `docs/content-schema.md` dan `data/recipes/`.
- Setiap `ingredients[].name` di `recipes.json` wajib ada di `ingredients.json`.
- Target dataset MVP: **60 resep**, **~120 ingredient kanonik**, fokus masakan
  Indonesia, canonical name bahasa Inggris + alias bahasa Indonesia.
- Resep ditulis original → field `source: "original"` (hindari isu lisensi).

---

## 10. Definition of Done (per task)

Task dianggap selesai bila:
- Tanggung jawab jelas, mengikuti dependency rules (§4).
- Tidak ada business logic di layer yang salah.
- Typing memadai (Pydantic / TS types).
- Test ada bila menyentuh logic (unit untuk engine, integration untuk API,
  component untuk React).
- `ruff` clean (backend), `pnpm lint` + `pnpm typecheck` clean (frontend),
  `pytest`/`vitest` hijau.
- Error state ditangani bila relevan.
- Tidak overengineer (abstraction hanya bila kurangi kompleksitas).

---

## 11. Anti-Pattern (jangan dibuat)

- Route yang berisi seluruh algoritma recommendation.
- Component `RecipePage.tsx` yang isinya API request + normalisasi + scoring + UI.
- `openai_service.py` yang menentukan ranking.
- Memindahkan business logic ke frontend.
- Menambah library besar untuk kebutuhan kecil.
- Mengubah folder structure luas tanpa alasan.
- Commit `.env`, secret, `node_modules`, `.venv`.

---

## 12. Alur Kerja Rekomendasi (untuk agent)

1. Baca PRD + 3 dok arsitektur + content-schema + roadmap + task-breakdown.
2. Identifikasi layer yang bertanggung jawab (component-architecture §32 Folder Ownership).
3. Cari komponen/service yang sudah ada — **reuse sebelum buat abstraction baru**.
4. Cek context7 bila pakai library/API yang belum pasti (§6).
5. Implementasi perubahan sekecil mungkin.
6. Tambah/update test (§10).
7. Jalankan lint + typecheck + test.
8. Periksa dependency boundary (§4).
9. Commit per task (§7).
10. Lapor progress, tunggu instruksi push.

---

## 13. Pertanyaan Terbuka (jawab setelah MVP stabil)

Diambil dari PRD §26, dicatat agar tidak mengganggu MVP:
1. Apakah staples otomatis tersedia? → **SUDAH DIJAWAB (ya, delta v1.1)**.
2. Bobot bahan penting? → **SUDAH DIJAWAB (MVP bobot rata)**.
3. Resep dengan sedikit missing vs raw% tinggi? → ranking tie-breaker sudah tangani
   (missing count ASC).
4. Kuantitas bahan dihitung? → **Out of scope MVP** (V1.1).
5. Lisensi/sumber resep saat dataset besar? → `source: "original"` saat ini.
6. Rate limiting / publikasi API? → simple in-memory limit opsional di phase 6.
