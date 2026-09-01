# Technical Architecture — Smart Living API

**Versi:** 1.0  
**Status:** Draf Implementasi MVP  
**Dokumen Terkait:** `prd.md`  
**Tujuan Dokumen:** Menjadi acuan teknis untuk membangun Smart Living API + Interactive Demo secara konsisten, teruji, dan mudah dikembangkan oleh developer maupun AI Agent.

---

## 1. Ringkasan Arsitektur

Smart Living menggunakan pendekatan **API-first** dengan frontend sebagai salah satu client dari backend.

Arsitektur MVP:

```text
┌──────────────────────────────┐
│      Interactive Web App     │
│      Next.js + TypeScript    │
└──────────────┬───────────────┘
               │ HTTPS / JSON
               ▼
┌──────────────────────────────┐
│        Smart Living API      │
│      FastAPI / Node API      │
├──────────────────────────────┤
│ HTTP / Validation Layer      │
│ Application / Use Case       │
│ Ingredient Normalizer        │
│ Recommendation Service       │
│ Deterministic Matching       │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Recipe Data   │  │ Optional AI  │
│ JSON / DB     │  │ Service      │
└──────────────┘  └──────────────┘
```

Prinsip utama:

1. **Deterministic matching adalah core MVP.**
2. **Frontend tidak boleh mengakses database secara langsung.**
3. **Business logic tidak ditempatkan di controller/route.**
4. **AI bersifat opsional dan berada di balik service boundary.**
5. **Schema request/response menjadi kontrak antara frontend dan API.**
6. **Komponen inti harus mudah diuji tanpa menjalankan server.**

---

## 2. Tujuan Teknis

Arsitektur harus:

- sederhana untuk MVP portfolio;
- mudah dijalankan secara lokal;
- mudah dipahami reviewer;
- mudah diuji otomatis;
- memungkinkan frontend dan backend dikembangkan relatif independen;
- memungkinkan penggantian dataset JSON ke PostgreSQL;
- memungkinkan AI ditambahkan tanpa mengubah recommendation core;
- ramah terhadap pengembangan menggunakan AI Agent seperti OpenCode.

---

## 3. Keputusan Teknologi

### 3.1 Rekomendasi Stack

Untuk proyek ini direkomendasikan:

| Area | Teknologi |
|---|---|
| Frontend | Next.js + TypeScript |
| Styling | Tailwind CSS |
| Backend | Python + FastAPI |
| Validation | Pydantic |
| Data MVP | JSON version-controlled |
| Database masa depan | PostgreSQL |
| API Docs | OpenAPI / Swagger |
| Testing Backend | Pytest |
| Testing Frontend | Vitest + React Testing Library |
| E2E | Playwright |
| Package / Runtime | pnpm + Node.js untuk web, uv atau pip untuk API |
| AI | OpenAI API sebagai integration opsional |
| Containerization | Docker |
| CI | GitHub Actions |
| Deployment | Vercel untuk web + platform container/server untuk API |

> Catatan: Node.js + Fastify juga valid. Dokumen ini menggunakan FastAPI sebagai baseline agar kontrak API dan validasi request/response mudah dieksplorasi.

---

## 4. Arsitektur Repository

Struktur yang direkomendasikan:

```text
smart-living/
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── hooks/
│   │   └── tests/
│   │
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   │   └── v1/
│       │   ├── core/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── repositories/
│       │   ├── domain/
│       │   └── main.py
│       └── tests/
│
├── data/
│   └── recipes/
│       ├── recipes.json
│       └── ingredients.json
│
├── docs/
│   ├── prd.md
│   ├── technical-architecture.md
│   ├── component-architecture.md
│   ├── content-schema.md
│   ├── development-roadmap.md
│   └── implementation-task-breakdown.md
│
├── .github/
│   └── workflows/
│
├── docker/
├── .env.example
├── README.md
└── docker-compose.yml
```

### Prinsip struktur

`domain/` berisi aturan bisnis inti.

`services/` mengatur use case aplikasi.

`repositories/` menangani akses data.

`api/` menangani HTTP.

Frontend hanya menggunakan API publik.

---

## 5. Layer Architecture Backend

Backend menggunakan pemisahan layer berikut:

```text
HTTP Request
    │
    ▼
Route / Controller
    │
    ▼
Schema Validation
    │
    ▼
Application Service
    │
    ├───────────────┐
    ▼               ▼
Normalizer     Recommendation Engine
                    │
                    ▼
              Recipe Repository
                    │
                    ▼
                Recipe Data
```

### 5.1 Route / Controller

Tanggung jawab:

- menerima HTTP request;
- menjalankan validation;
- memanggil application service;
- mengubah hasil service menjadi HTTP response;
- tidak mengandung algoritma ranking.

### 5.2 Application Service

Contoh:

```text
RecommendationService
```

Tanggung jawab:

1. menerima ingredient input;
2. melakukan normalisasi;
3. mengambil recipe candidates;
4. memanggil matching engine;
5. mengurutkan hasil;
6. membangun response domain.

### 5.3 Matching Engine

Tanggung jawab hanya pada business logic:

```text
input ingredients
        ↓
normalize
        ↓
compare recipe
        ↓
calculate score
        ↓
identify available/missing
        ↓
ranking
```

Matching engine harus dapat digunakan tanpa FastAPI.

### 5.4 Repository

Repository menyediakan abstraction:

```python
class RecipeRepository:
    def get_all(self):
        ...

    def get_by_id(self, recipe_id):
        ...
```

Implementasi awal:

```text
JsonRecipeRepository
```

Implementasi masa depan:

```text
PostgresRecipeRepository
```

Service tidak boleh bergantung langsung pada format file JSON.

---

## 6. Domain Model

### 6.1 Ingredient

```json
{
  "name": "egg",
  "displayName": "Egg",
  "aliases": ["eggs", "telur"],
  "category": "protein"
}
```

### 6.2 Recipe

```json
{
  "id": "recipe_001",
  "name": "Chicken Carrot Omelette",
  "description": "Omelet praktis dengan ayam dan wortel.",
  "ingredients": [
    {
      "name": "egg",
      "required": true
    },
    {
      "name": "chicken",
      "required": true
    },
    {
      "name": "carrot",
      "required": true
    },
    {
      "name": "onion",
      "required": false
    }
  ],
  "cookingTimeMinutes": 15,
  "difficulty": "easy",
  "steps": [
    "Siapkan semua bahan.",
    "Masak ayam dan wortel.",
    "Tambahkan telur.",
    "Masak hingga matang lalu sajikan."
  ]
}
```

---

## 7. Ingredient Normalization

Normalisasi MVP harus sederhana, deterministik, dan dapat dijelaskan.

Contoh:

```text
" telur "       → "egg"
"eggs"          → "egg"
"TELUR"         → "egg"
"chicken breast"→ "chicken"
"carrots"       → "carrot"
```

### Proses

```text
Raw Input
   ↓
Trim whitespace
   ↓
Lowercase
   ↓
Split input
   ↓
Alias lookup
   ↓
Canonical ingredient
```

### Aturan

- Gunakan canonical ingredient name.
- Alias disimpan dalam kamus/data ingredient.
- Jangan menggunakan LLM untuk normalisasi dasar pada MVP.
- Input yang tidak dikenali tidak boleh dipetakan secara sembarang.

Contoh hasil:

```json
{
  "normalizedIngredients": [
    "egg",
    "chicken",
    "carrot"
  ],
  "unknownIngredients": []
}
```

---

## 8. Recommendation Engine

### 8.1 Formula MVP

```text
matchPercentage =
matchedRequiredIngredients /
totalRequiredIngredients
× 100
```

Contoh:

```text
User:
egg, chicken, carrot

Recipe:
egg, chicken, carrot, onion

Matched = 3
Required = 4

Match = 75%
```

### 8.2 Available Ingredients

Bahan recipe yang ada di input user:

```text
availableIngredients =
recipe.requiredIngredients ∩ userIngredients
```

### 8.3 Missing Ingredients

```text
missingIngredients =
recipe.requiredIngredients - userIngredients
```

### 8.4 Optional Ingredients

Bahan `required: false` tidak dihitung sebagai kewajiban untuk mendapatkan kecocokan 100%.

### 8.5 Ranking

Ranking MVP dapat menggunakan urutan:

1. `matchPercentage` tertinggi;
2. jumlah missing ingredients paling sedikit;
3. waktu memasak tercepat;
4. recipe ID sebagai tie-breaker deterministik.

Contoh:

```text
sort(
  -matchPercentage,
  missingCount,
  cookingTimeMinutes,
  recipeId
)
```

Dengan ini dua request yang sama akan menghasilkan urutan yang sama.

---

## 9. API Contract

### 9.1 POST /api/v1/recommendations

Request:

```json
{
  "ingredients": [
    "telur",
    "ayam",
    "wortel"
  ],
  "limit": 5
}
```

Validation:

- `ingredients` wajib;
- minimal 1 item;
- `limit` default 5;
- `limit` maksimum 10;
- duplikasi ingredient dihapus setelah normalisasi.

Response:

```json
{
  "query": {
    "ingredients": [
      "egg",
      "chicken",
      "carrot"
    ]
  },
  "results": [
    {
      "id": "recipe_001",
      "name": "Chicken Carrot Omelette",
      "description": "Omelet praktis dengan ayam dan wortel.",
      "matchPercentage": 75,
      "availableIngredients": [
        "egg",
        "chicken",
        "carrot"
      ],
      "missingIngredients": [
        "onion"
      ],
      "cookingTimeMinutes": 15,
      "difficulty": "easy",
      "ingredients": [
        "egg",
        "chicken",
        "carrot",
        "onion"
      ],
      "steps": [
        "Siapkan semua bahan.",
        "Masak ayam dan wortel.",
        "Tambahkan telur.",
        "Masak hingga matang lalu sajikan."
      ]
    }
  ],
  "meta": {
    "count": 1,
    "limit": 5
  }
}
```

### 9.2 GET /api/v1/recipes/{id}

Mengembalikan detail recipe berdasarkan ID.

### 9.3 GET /api/v1/ingredients

Mengembalikan daftar ingredient canonical + alias untuk kebutuhan autocomplete/frontend.

### 9.4 GET /api/v1/health

Response:

```json
{
  "status": "ok"
}
```

---

## 10. API Error Contract

Format error harus konsisten:

```json
{
  "error": {
    "code": "INVALID_INGREDIENTS",
    "message": "Bahan harus berisi setidaknya satu item.",
    "details": null
  }
}
```

Contoh kode:

```text
INVALID_INGREDIENTS
INGREDIENT_NOT_FOUND
RECIPE_NOT_FOUND
VALIDATION_ERROR
INTERNAL_ERROR
```

Jangan mengembalikan stack trace kepada client production.

---

## 11. Frontend Architecture

Frontend adalah client API, bukan tempat business logic utama.

Struktur:

```text
Page
 │
 ├── IngredientInput
 │
 ├── RecommendationList
 │      └── RecipeCard
 │
 └── RecipeDetail
```

### State

Frontend minimal membutuhkan state:

```text
ingredients
loading
results
selectedRecipe
error
```

### Flow

```text
User Input
   ↓
Submit
   ↓
HTTP POST /recommendations
   ↓
Loading
   ↓
Success → Render cards
   ↓
Failure → Render error
```

### UI State

Harus tersedia:

- initial;
- loading;
- success;
- empty;
- error.

---

## 12. API Showcase pada Frontend

Frontend portfolio harus memiliki area:

### Contoh Request

```http
POST /api/v1/recommendations
Content-Type: application/json
```

```json
{
  "ingredients": ["egg", "chicken", "carrot"],
  "limit": 5
}
```

### Contoh Response

Tampilkan JSON yang dapat dibaca developer.

### Arsitektur

Tampilkan diagram:

```text
Browser
   ↓
Next.js
   ↓
Smart Living API
   ↓
Matching Engine
   ↓
Recipe Dataset
```

Tujuan section ini adalah membuat reviewer dapat memahami engineering project tanpa membaca source code terlebih dahulu.

---

## 13. AI Integration Boundary

AI tidak boleh masuk ke recommendation engine utama pada MVP.

Arsitektur masa depan:

```text
Frontend
   │
   ▼
API
   │
   ├── Deterministic Recommendation
   │
   └── AI Service
           │
           ▼
       OpenAI API
```

AI Service dapat menangani:

- natural language ingredient parsing;
- recipe explanation;
- ingredient substitution;
- conversational cooking assistant.

Contoh:

```text
User:
"Saya punya dua telur, setengah wortel,
dan sisa ayam panggang."

        ↓

AI Ingredient Parser

        ↓

{
  "ingredients": [
    {"name": "egg", "quantity": 2},
    {"name": "carrot", "quantity": 0.5},
    {"name": "chicken", "quantity": null}
  ]
}

        ↓

Deterministic Recommendation Engine
```

### Prinsip penting

AI menghasilkan atau mentransformasi data.

Deterministic service mengambil keputusan ranking utama.

Dengan pendekatan ini, AI dapat diganti tanpa menulis ulang core recommendation engine.

---

## 14. Kontrak Service AI

Gunakan interface konseptual:

```python
class IngredientParser:
    def parse(self, text: str) -> ParsedIngredients:
        ...
```

Implementasi:

```text
ManualIngredientParser
AIIngredientParser
```

Dengan abstraction ini, aplikasi dapat menggunakan parser manual atau AI tanpa mengubah use case utama.

---

## 15. Data Strategy

### MVP

Gunakan JSON version-controlled.

Contoh:

```text
data/recipes/recipes.json
data/recipes/ingredients.json
```

Keuntungan:

- cepat;
- mudah diperiksa;
- mudah diubah;
- tidak membutuhkan database setup;
- cocok untuk dataset 50–100 resep.

### Migrasi PostgreSQL

Gunakan ketika:

- jumlah recipe meningkat;
- filtering menjadi kompleks;
- ada user accounts;
- ada pantry;
- ada personalization;
- ada analytics yang persisten.

Repository abstraction harus membuat migrasi tidak mengubah business logic.

---

## 16. Caching

MVP tidak membutuhkan cache kompleks.

Namun struktur dapat disiapkan agar kelak mendukung:

```text
Client
 ↓
API
 ↓
Cache
 ↓
Recommendation Service
```

Pada MVP:

- recipe dataset dimuat saat startup atau melalui repository;
- hasil matching dihitung in-memory;
- tidak perlu Redis kecuali ada kebutuhan performa nyata.

---

## 17. Security

### MVP

- Validasi semua payload.
- Batasi ukuran request.
- Jangan expose API key.
- CORS hanya mengizinkan domain yang diperlukan.
- Gunakan HTTPS pada deployment.
- Jangan menyimpan input user jika tidak diperlukan.

### AI

OpenAI/API secret hanya berada di backend:

```text
Frontend ❌ → OpenAI
Frontend ✅ → Smart Living API → OpenAI
```

---

## 18. Observability

Log dasar:

```text
request_id
method
path
status_code
duration_ms
```

Untuk recommendation:

```text
ingredient_count
result_count
```

Jangan log secret atau data pribadi yang tidak diperlukan.

Metrik awal:

- request count;
- error rate;
- p50/p95 latency;
- empty recommendation rate.

---

## 19. Performance Target

Target MVP:

```text
p50 < 200 ms
p95 < 500 ms
```

Untuk deterministic recommendation terhadap dataset lokal 50–100 recipes, target ini seharusnya realistis.

Benchmark harus dilakukan berdasarkan implementasi nyata, bukan asumsi.

AI request memiliki target terpisah karena latency provider eksternal dapat berbeda.

---

## 20. Testing Strategy

### 20.1 Unit Test

Prioritas utama:

- normalization;
- alias mapping;
- matching;
- percentage calculation;
- missing ingredients;
- available ingredients;
- ranking;
- tie-breaker;
- limit.

Contoh:

```text
Input:
egg, chicken, carrot

Recipe:
egg, chicken, carrot, onion

Expected:
75%
```

### 20.2 API Integration Test

Test:

```text
POST /recommendations
```

Skenario:

- valid input;
- empty array;
- missing field;
- invalid limit;
- unknown ingredient;
- no matching recipe.

### 20.3 Frontend Test

Test:

- input rendering;
- submit interaction;
- loading state;
- result rendering;
- empty state;
- error state.

### 20.4 E2E

Playwright:

```text
Open site
→ input ingredients
→ click Find Recipes
→ recommendations appear
→ open recipe detail
```

---

## 21. Definition of Done Teknis

Fitur MVP dianggap selesai ketika:

- API dapat dijalankan lokal;
- frontend dapat dijalankan lokal;
- API contract terdokumentasi;
- recipe dataset memiliki minimal 50 resep berkualitas;
- matching engine memiliki unit test;
- API memiliki integration test;
- frontend memiliki loading/error/empty state;
- frontend menggunakan API nyata;
- response schema tervalidasi;
- health endpoint tersedia;
- `.env.example` tersedia;
- README memiliki setup instructions;
- aplikasi dapat dibangun tanpa konfigurasi rahasia di source code.

---

## 22. Environment Variables

Contoh `.env.example`:

```env
# API
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# AI - optional
OPENAI_API_KEY=
OPENAI_MODEL=
```

Jangan commit `.env`.

---

## 23. Docker Strategy

MVP dapat menggunakan:

```text
docker-compose.yml
```

Service:

```text
web
api
```

Database belum wajib.

Masa depan:

```text
web
api
postgres
redis
```

Namun jangan menambah service hanya untuk terlihat kompleks. Setiap komponen harus mempunyai kebutuhan yang jelas.

---

## 24. CI Pipeline

GitHub Actions:

```text
Push / Pull Request
       ↓
Lint
       ↓
Type Check
       ↓
Unit Test
       ↓
Integration Test
       ↓
Build
```

Frontend:

```text
npm/pnpm lint
npm/pnpm typecheck
npm/pnpm test
npm/pnpm build
```

Backend:

```text
ruff
pytest
```

---

## 25. Deployment Architecture

Target awal:

```text
User Browser
    │
    ▼
Frontend Hosting
    │
    ▼
Public API
    │
    └── Recipe Dataset
```

AI:

```text
Public API
    │
    ▼
AI Provider
```

Tidak perlu Kubernetes, microservices, atau service mesh pada MVP.

Untuk portfolio, deployment sederhana tetapi stabil lebih bernilai daripada arsitektur yang terlalu kompleks.

---

## 26. API Versioning

Gunakan:

```text
/api/v1/
```

Contoh:

```text
/api/v1/recommendations
```

Ketika terjadi breaking change:

```text
/api/v2/recommendations
```

Hindari breaking change pada endpoint v1 selama client masih menggunakannya.

---

## 27. Non-Goals Teknis MVP

Jangan implementasikan sebelum ada kebutuhan produk:

- microservices;
- event-driven architecture;
- Kubernetes;
- real-time websocket;
- Redis;
- vector database;
- RAG;
- computer vision;
- authentication kompleks;
- payment;
- native mobile application.

Fokus:

```text
Ingredient Input
→ Normalization
→ Matching
→ Ranking
→ API
→ Interactive UI
```

---

## 28. Risiko Teknis

### Dataset terlalu kecil

Mitigasi: kurasi 50–100 recipes dan prioritaskan variasi ingredient.

### Ingredient alias buruk

Mitigasi: canonical dictionary + alias test.

### Ranking terasa tidak relevan

Mitigasi: benchmark dengan test cases nyata dan review hasil secara manual.

### AI menambah kompleksitas

Mitigasi: isolasi AI service dan jadikan feature flag/opsional.

### Frontend dan backend contract drift

Mitigasi:

- schema bersama;
- OpenAPI;
- integration test;
- contoh response yang version-controlled.

---

## 29. Engineering Principles untuk AI Agent

AI Agent yang mengerjakan repository harus mengikuti prinsip:

### Jangan mengubah architecture tanpa alasan

Sebelum menambah dependency atau layer baru, periksa apakah masalah tersebut dapat diselesaikan dalam struktur yang sudah ada.

### Business logic harus testable

Jangan menaruh matching algorithm di HTTP route.

### Jangan mengarang data

Recipe harus berasal dari dataset yang tersedia atau sumber yang jelas.

### Hindari overengineering

MVP portfolio tidak membutuhkan sistem distributed.

### Perubahan harus incremental

Lebih baik membuat:

```text
normalize → test → matching → test → API → test
```

daripada menghasilkan seluruh sistem sekaligus tanpa validasi.

### Setiap fitur harus memiliki acceptance criteria

AI Agent harus mengacu pada PRD dan dokumen arsitektur sebelum implementasi.

---

## 30. Urutan Implementasi

Urutan teknis yang direkomendasikan:

### Phase 1 — Foundation

- setup repository;
- setup backend;
- setup frontend;
- setup linting;
- setup testing;
- buat environment configuration.

### Phase 2 — Data

- definisikan ingredient schema;
- definisikan recipe schema;
- buat dataset awal;
- buat repository.

### Phase 3 — Core Engine

- normalization;
- matching;
- scoring;
- ranking;
- unit test.

### Phase 4 — API

- POST recommendations;
- GET recipe;
- GET ingredients;
- health endpoint;
- validation;
- error handling;
- OpenAPI.

### Phase 5 — Frontend

- landing page;
- ingredient input;
- result cards;
- recipe detail;
- loading;
- error;
- empty state.

### Phase 6 — Portfolio Layer

- API showcase;
- architecture diagram;
- README;
- screenshots;
- technical decisions;
- deployment.

### Phase 7 — AI Enhancement

Hanya setelah core MVP stabil:

- AI ingredient parser;
- explanation;
- substitution;
- conversational assistant.

---

## 31. Contoh Dependency Flow

```text
Frontend
  ↓
HTTP Client
  ↓
API Route
  ↓
Recommendation Service
  ↓
Ingredient Normalizer
  ↓
Recipe Repository
  ↓
Matching Engine
  ↓
Ranking
  ↓
Response Schema
  ↓
Frontend
```

Tidak diperbolehkan:

```text
Frontend
  ↓
Database
```

atau:

```text
API Route
  ↓
LLM
  ↓
langsung menghasilkan ranking
```

untuk core MVP.

---

## 32. Keputusan Arsitektur Utama

| Keputusan | Pilihan | Alasan |
|---|---|---|
| Architecture | API-first | Menonjolkan kemampuan backend/API |
| Core logic | Deterministic | Konsisten dan mudah diuji |
| Data | JSON dulu | Cepat untuk MVP |
| DB | PostgreSQL nanti | Saat complexity meningkat |
| AI | Service terpisah | Mudah diisolasi |
| Frontend | Next.js | Showcase full-stack |
| Backend | FastAPI | Validation dan OpenAPI kuat |
| API versioning | `/v1` | Menjaga kompatibilitas |
| Deployment | Sederhana | Menghindari overengineering |
| Testing | Unit + integration + E2E | Menunjukkan engineering maturity |

---

## 33. Diagram End-to-End

```text
                 ┌──────────────────┐
                 │      User        │
                 └────────┬─────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Next.js Web App  │
                └─────────┬──────────┘
                          │
                     HTTPS / JSON
                          │
                          ▼
                ┌────────────────────┐
                │  Smart Living API  │
                └─────────┬──────────┘
                          │
                 ┌────────┴─────────┐
                 ▼                  ▼
        ┌────────────────┐  ┌────────────────┐
        │ Ingredient     │  │ Recommendation │
        │ Normalizer     │  │ Service        │
        └────────┬───────┘  └───────┬────────┘
                 │                  │
                 └────────┬─────────┘
                          ▼
                ┌────────────────────┐
                │ Deterministic      │
                │ Matching Engine    │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Recipe Repository  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Recipe Dataset     │
                │ JSON / PostgreSQL  │
                └────────────────────┘

                  Future AI Boundary
                          │
                          ▼
                ┌────────────────────┐
                │    AI Service      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   OpenAI API       │
                └────────────────────┘
```

---

## 34. Final Technical Direction

Smart Living MVP harus tetap kecil secara arsitektural tetapi memiliki batas yang jelas.

Core:

```text
Manual Ingredient Input
        ↓
Normalization
        ↓
Deterministic Matching
        ↓
Ranking
        ↓
REST API
        ↓
Interactive Frontend
```

AI:

```text
Natural Language
        ↓
AI Parsing
        ↓
Structured Ingredients
        ↓
Deterministic Matching
```

Dengan demikian, proyek dapat berkembang dari demo sederhana menjadi platform recommendation yang lebih cerdas tanpa perlu membuang core architecture.

---

## 35. Hubungan dengan PRD

PRD menjawab:

> **Apa yang dibangun dan mengapa?**

Dokumen arsitektur ini menjawab:

> **Bagaimana sistem tersebut dibangun?**

Keduanya harus dibaca bersama sebelum implementasi dimulai.

Source of truth:

```text
PRD
 ↓
Technical Architecture
 ↓
Implementation
 ↓
Testing
 ↓
Deployment
```
