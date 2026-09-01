# Component Architecture — Smart Living

**Versi:** 1.0  
**Status:** Draf Implementasi MVP  
**Dokumen Terkait:** `prd.md`, `technical-architecture.md`  
**Tujuan Dokumen:** Menentukan struktur komponen, tanggung jawab, dependency, dan batas antar-komponen agar implementasi Smart Living tetap terorganisasi dan mudah dikembangkan.

---

## 1. Tujuan Component Architecture

Dokumen ini menjawab pertanyaan:

> **"Setelah arsitektur teknis ditentukan, komponen apa saja yang harus dibuat dan bagaimana masing-masing komponen saling berhubungan?"**

Fokus utama:

- memisahkan tanggung jawab setiap komponen;
- mencegah business logic tersebar di banyak tempat;
- menjaga frontend dan backend tetap modular;
- memudahkan testing;
- memudahkan AI Agent memahami lokasi kode yang benar;
- memungkinkan fitur AI ditambahkan tanpa merusak core MVP.

---

## 2. Prinsip Arsitektur Komponen

### 2.1 Single Responsibility

Setiap komponen harus mempunyai tanggung jawab utama yang jelas.

Contoh:

```text
IngredientInput
→ menangani input UI

RecommendationService
→ mengorkestrasi proses rekomendasi

MatchingEngine
→ menghitung kecocokan

RecipeRepository
→ mengambil data resep
```

### 2.2 Dependency Direction

Dependency utama harus mengalir ke arah domain/application, bukan sebaliknya.

```text
UI → API → Application → Domain
                  ↓
             Repository
```

Komponen domain tidak boleh mengetahui detail HTTP, database, atau React.

### 2.3 Separation of Concerns

Jangan mencampur:

- UI logic;
- HTTP logic;
- business logic;
- data access;
- AI integration.

### 2.4 Explicit Contracts

Komunikasi antarkomponen menggunakan contract/schema yang eksplisit.

### 2.5 Composition Over Complexity

Komponen kecil boleh digabung bila abstraction tambahan tidak memberikan manfaat nyata.

---

# 3. Arsitektur Komponen Tingkat Tinggi

```text
┌────────────────────────────────────────────────────┐
│                    FRONTEND                        │
│                                                    │
│  Page                                             │
│   │                                                │
│   ├── IngredientInput                              │
│   │       │                                        │
│   │       ▼                                        │
│   │   Recommendation API Client                    │
│   │       │                                        │
│   └───────┼──────────────────────┐                 │
│           ▼                      ▼                 │
│    RecommendationList       RecipeDetail           │
│           │                                        │
│           ▼                                        │
│       RecipeCard                                   │
└───────────────────┬────────────────────────────────┘
                    │ HTTP / JSON
                    ▼
┌────────────────────────────────────────────────────┐
│                     BACKEND                        │
│                                                    │
│  API Route                                         │
│      │                                             │
│      ▼                                             │
│  Request / Response Schema                         │
│      │                                             │
│      ▼                                             │
│  Recommendation Service                            │
│      │                                             │
│      ├── Ingredient Normalizer                     │
│      │                                             │
│      ├── Matching Engine                           │
│      │                                             │
│      └── Recipe Repository                         │
│               │                                    │
│               ▼                                    │
│          Recipe Dataset                            │
│                                                    │
│  Optional AI Service ───────► AI Provider           │
└────────────────────────────────────────────────────┘
```

---

# 4. Struktur Folder Final

Struktur awal yang direkomendasikan:

```text
smart-living/
│
├── apps/
│   │
│   ├── web/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── recipes/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── api-docs/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ingredients/
│   │   │   ├── recommendations/
│   │   │   ├── recipes/
│   │   │   ├── ui/
│   │   │   └── showcase/
│   │   │
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   ├── utils/
│   │   │   └── constants/
│   │   │
│   │   ├── hooks/
│   │   ├── types/
│   │   └── tests/
│   │
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   │
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── routes/
│       │   │       │   ├── recommendations.py
│       │   │       │   ├── recipes.py
│       │   │       │   ├── ingredients.py
│       │   │       │   └── health.py
│       │   │       └── router.py
│       │   │
│       │   ├── schemas/
│       │   │   ├── recommendation.py
│       │   │   ├── recipe.py
│       │   │   ├── ingredient.py
│       │   │   └── error.py
│       │   │
│       │   ├── services/
│       │   │   ├── recommendation_service.py
│       │   │   ├── ingredient_normalizer.py
│       │   │   └── ai/
│       │   │       ├── base.py
│       │   │       └── openai_service.py
│       │   │
│       │   ├── domain/
│       │   │   ├── matching/
│       │   │   │   ├── engine.py
│       │   │   │   ├── scoring.py
│       │   │   │   └── ranking.py
│       │   │   └── models/
│       │   │       ├── ingredient.py
│       │   │       └── recipe.py
│       │   │
│       │   ├── repositories/
│       │   │   ├── base.py
│       │   │   └── json_recipe_repository.py
│       │   │
│       │   └── core/
│       │       ├── config.py
│       │       ├── logging.py
│       │       └── errors.py
│       │
│       └── tests/
│           ├── unit/
│           └── integration/
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
├── docker/
├── .env.example
├── docker-compose.yml
└── README.md
```

---

# 5. Frontend Component Architecture

## 5.1 Halaman Utama

```text
app/page.tsx
```

Tanggung jawab:

- menyusun layout halaman utama;
- menggabungkan komponen fitur;
- tidak menangani algoritma rekomendasi.

Struktur:

```text
HomePage
├── HeroSection
├── IngredientInput
├── RecommendationSection
│   └── RecommendationList
├── ApiShowcase
├── ArchitectureShowcase
└── Footer
```

---

# 6. Komponen Ingredient Input

Folder:

```text
components/ingredients/
```

Komponen utama:

```text
IngredientInput
IngredientTag
IngredientInputHelp
```

## IngredientInput

Tanggung jawab:

- menerima text input;
- mendukung input seperti:

```text
telur, ayam, wortel
```

- submit dengan tombol;
- submit dengan Enter;
- menampilkan ingredient yang akan dicari;
- melakukan validasi UI ringan.

Tidak bertanggung jawab atas:

- recipe matching;
- normalisasi canonical;
- API request langsung bila logic tersebut dapat dipisahkan ke client layer.

Flow:

```text
User
 ↓
IngredientInput
 ↓
onSubmit(ingredients)
 ↓
Recommendation Hook
```

---

# 7. Recommendation Components

Folder:

```text
components/recommendations/
```

Komponen:

```text
RecommendationSection
RecommendationList
RecommendationCard
RecommendationSkeleton
RecommendationEmpty
RecommendationError
MatchBadge
IngredientStatus
```

## RecommendationList

Tanggung jawab:

- menerima array recommendation;
- melakukan rendering;
- tidak menghitung match percentage.

Contoh props:

```ts
type RecommendationListProps = {
  results: Recommendation[];
};
```

## RecommendationCard

Menampilkan:

```text
Recipe Name
Match Percentage
Available Ingredients
Missing Ingredients
Cooking Time
Difficulty
View Recipe
```

Contoh struktur visual:

```text
┌─────────────────────────────┐
│ Chicken Carrot Omelette     │
│ 75% Match                   │
│                             │
│ ✓ Egg                       │
│ ✓ Chicken                   │
│ ✓ Carrot                    │
│ ! Onion                     │
│                             │
│ 15 min · Easy               │
│                             │
│ [View Recipe]               │
└─────────────────────────────┘
```

---

# 8. Recipe Components

Folder:

```text
components/recipes/
```

Komponen:

```text
RecipeDetail
RecipeHeader
RecipeIngredientList
RecipeInstructionList
RecipeMeta
```

## RecipeDetail

Menampilkan seluruh informasi recipe:

- nama;
- deskripsi;
- match percentage bila berasal dari recommendation;
- bahan;
- bahan yang tersedia;
- bahan yang kurang;
- waktu;
- tingkat kesulitan;
- langkah memasak.

---

# 9. Shared UI Components

Folder:

```text
components/ui/
```

Contoh:

```text
Button
Input
Badge
Card
Dialog
Skeleton
Alert
Spinner
```

Komponen di sini harus bersifat generik.

Jangan menaruh:

```text
RecipeCard
IngredientNormalizer
RecommendationLogic
```

di folder `ui/`.

---

# 10. API Showcase Components

Folder:

```text
components/showcase/
```

Komponen:

```text
ApiShowcase
RequestExample
ResponseExample
ArchitectureDiagram
TechStack
```

Tujuan:

Menampilkan kemampuan engineering dalam portfolio tanpa mencampurkannya dengan fitur recommendation utama.

---

# 11. Frontend API Client

Folder:

```text
lib/api/
```

File:

```text
client.ts
recommendations.ts
recipes.ts
ingredients.ts
```

Contoh:

```ts
export async function getRecommendations(
  ingredients: string[],
  limit = 5
) {
  // POST /api/v1/recommendations
}
```

Frontend component tidak boleh menyusun URL API secara manual di banyak file.

Gunakan satu API client layer.

---

# 12. Frontend Hooks

Folder:

```text
hooks/
```

Contoh:

```text
useRecommendations.ts
useRecipe.ts
```

## useRecommendations

Tanggung jawab:

- mengelola request;
- loading;
- success;
- error;
- hasil recommendation.

Konseptual:

```text
IngredientInput
      ↓
useRecommendations
      ↓
API Client
      ↓
Smart Living API
```

---

# 13. Backend API Components

Folder:

```text
apps/api/app/api/v1/routes/
```

Komponen:

```text
recommendations.py
recipes.py
ingredients.py
health.py
```

## recommendations.py

Hanya menangani:

```text
HTTP request
→ validation
→ service call
→ HTTP response
```

Tidak boleh:

```text
menghitung match percentage
```

langsung di route.

---

# 14. Request/Response Schema Components

Folder:

```text
schemas/
```

Tujuan:

- validasi request;
- validasi response;
- definisi kontrak API;
- menghasilkan dokumentasi OpenAPI.

Contoh:

```python
class RecommendationRequest(BaseModel):
    ingredients: list[str]
    limit: int = 5
```

Response:

```python
class RecommendationItem(BaseModel):
    id: str
    name: str
    matchPercentage: int
    availableIngredients: list[str]
    missingIngredients: list[str]
    cookingTimeMinutes: int
    difficulty: str
    ingredients: list[str]
    steps: list[str]
```

---

# 15. Recommendation Service

File:

```text
services/recommendation_service.py
```

Ini adalah orchestration layer.

Tanggung jawab:

```text
request
 ↓
normalize ingredients
 ↓
get recipes
 ↓
calculate match
 ↓
rank
 ↓
limit results
 ↓
build response
```

Konseptual:

```python
class RecommendationService:

    def recommend(self, ingredients, limit=5):
        normalized = self.normalizer.normalize(ingredients)
        recipes = self.recipe_repository.get_all()

        results = self.matcher.match(
            normalized,
            recipes
        )

        ranked = self.ranker.rank(results)

        return ranked[:limit]
```

Service tidak boleh mengetahui detail file JSON.

---

# 16. Ingredient Normalizer

File:

```text
services/ingredient_normalizer.py
```

Tanggung jawab:

```text
raw input
→ canonical ingredient
```

Contoh:

```text
"Eggs" → "egg"
" telur " → "egg"
"Carrots" → "carrot"
```

Normalisasi harus deterministic.

---

# 17. Matching Engine

Folder:

```text
domain/matching/
```

Komponen:

```text
engine.py
scoring.py
ranking.py
```

## MatchingEngine

Input:

```text
user ingredients
+
recipe
```

Output:

```text
MatchResult
```

Contoh:

```python
MatchResult(
    recipe_id="recipe_001",
    match_percentage=75,
    available_ingredients=[
        "egg",
        "chicken",
        "carrot"
    ],
    missing_ingredients=[
        "onion"
    ]
)
```

Matching engine tidak mengetahui:

- HTTP;
- FastAPI;
- React;
- OpenAI;
- database connection.

---

# 18. Scoring Component

File:

```text
domain/matching/scoring.py
```

Tanggung jawab:

```text
menghitung match percentage
```

Formula:

```text
matched required ingredients
-------------------------------- × 100
total required ingredients
```

Contoh:

```text
3 / 4 × 100 = 75
```

Scoring harus pure function bila memungkinkan.

Contoh:

```python
def calculate_match_percentage(
    matched: int,
    required: int
) -> int:
    ...
```

---

# 19. Ranking Component

File:

```text
domain/matching/ranking.py
```

Tanggung jawab:

- mengurutkan MatchResult;
- menerapkan tie-breaker;
- menjaga hasil deterministic.

Urutan:

```text
1. Match percentage DESC
2. Missing ingredients ASC
3. Cooking time ASC
4. Recipe ID ASC
```

---

# 20. Recipe Repository

Folder:

```text
repositories/
```

Interface:

```text
base.py
```

Implementasi MVP:

```text
json_recipe_repository.py
```

Dependency:

```text
RecommendationService
        ↓
RecipeRepository interface
        ↓
JsonRecipeRepository
        ↓
recipes.json
```

Di masa depan:

```text
RecipeRepository interface
        ↓
PostgresRecipeRepository
        ↓
PostgreSQL
```

Service tidak perlu berubah.

---

# 21. Domain Models

Folder:

```text
domain/models/
```

Model:

```text
Ingredient
Recipe
MatchResult
```

Domain model harus bebas dari framework.

Hindari:

```python
from fastapi import ...
```

di domain.

---

# 22. AI Components

Folder:

```text
services/ai/
```

Komponen:

```text
base.py
openai_service.py
```

Interface konseptual:

```python
class IngredientParser:
    def parse(self, text: str):
        ...
```

Implementasi:

```text
ManualIngredientParser
AIIngredientParser
```

AI Service bertugas:

```text
Natural Language
        ↓
Structured Ingredients
```

Bukan:

```text
Natural Language
        ↓
langsung menentukan ranking recipe
```

---

# 23. AI Dependency Boundary

Arsitektur:

```text
RecommendationService
        │
        ├── Deterministic Path
        │
        └── Optional AI Path
                    │
                    ▼
              AI Provider
```

Untuk MVP:

```text
AI disabled
```

Untuk fase AI:

```text
AI enabled
```

Namun output AI harus dikonversi menjadi schema internal sebelum digunakan.

---

# 24. Dependency Matrix

| Komponen | Boleh bergantung pada | Tidak boleh bergantung pada |
|---|---|---|
| UI Component | UI primitives, types | database, domain service |
| API Client | HTTP client, types | database |
| API Route | schema, application service | repository langsung |
| Application Service | domain, repository interface | React, HTTP |
| Matching Engine | domain models | FastAPI, OpenAI |
| Scoring | primitive/domain data | HTTP, database |
| Ranking | MatchResult | frontend |
| Repository | domain models, data source | React |
| AI Service | provider SDK, schemas | frontend langsung |
| Domain Model | standard library | framework |

---

# 25. Dependency Rules

## Rule 1

Frontend hanya berbicara dengan API melalui API client.

## Rule 2

Route tidak boleh mengakses repository secara langsung untuk use case utama.

## Rule 3

Matching Engine tidak boleh melakukan HTTP request.

## Rule 4

Matching Engine tidak boleh memanggil LLM.

## Rule 5

Repository tidak boleh menentukan ranking recommendation.

## Rule 6

AI service tidak boleh menyimpan business decision utama.

## Rule 7

Shared types harus merepresentasikan contract, bukan implementasi internal.

---

# 26. Data Flow Recommendation

Alur lengkap:

```text
User
 │
 ▼
IngredientInput
 │
 ▼
useRecommendations()
 │
 ▼
API Client
 │
 ▼
POST /api/v1/recommendations
 │
 ▼
Request Schema
 │
 ▼
RecommendationService
 │
 ├──► IngredientNormalizer
 │
 ├──► RecipeRepository
 │
 └──► MatchingEngine
          │
          ├──► Scoring
          └──► Ranking
 │
 ▼
Response Schema
 │
 ▼
JSON Response
 │
 ▼
API Client
 │
 ▼
RecommendationList
 │
 ▼
RecipeCard
```

---

# 27. Data Flow Future AI

```text
User
 │
 ▼
Natural Language Input
 │
 ▼
API
 │
 ▼
AI Ingredient Parser
 │
 ▼
Validated Structured Ingredients
 │
 ▼
RecommendationService
 │
 ▼
Deterministic Matching Engine
 │
 ▼
Recommendations
```

AI menjadi preprocessing/enhancement layer, bukan pengganti core recommendation engine.

---

# 28. Component Communication Rules

Gunakan:

```text
Props
Callbacks
Hooks
API contracts
Service interfaces
```

Hindari global state untuk sesuatu yang cukup ditangani oleh local state.

Gunakan global state hanya ketika kebutuhan nyata muncul, misalnya:

```text
persistent preferences
pantry state
authentication
```

MVP tidak membutuhkan global state kompleks.

---

# 29. Error Ownership

Setiap layer menangani error pada level yang sesuai.

```text
API
→ HTTP errors

Service
→ business/application errors

Repository
→ data access errors

Frontend API client
→ network/API errors

UI
→ user-friendly presentation
```

Contoh:

```text
Repository error
        ↓
Service error
        ↓
API error response
        ↓
Frontend error state
```

---

# 30. Loading & Empty States

Frontend component harus memiliki state yang eksplisit.

### Loading

```text
RecommendationSkeleton
```

### Empty

```text
RecommendationEmpty
```

### Error

```text
RecommendationError
```

### Success

```text
RecommendationList
```

Jangan membuat satu component besar dengan conditional logic yang sulit dibaca.

---

# 31. Testing Boundary

Setiap boundary memiliki strategi test:

```text
Normalizer
→ Unit Test

Scoring
→ Unit Test

Ranking
→ Unit Test

Matching Engine
→ Unit Test

RecommendationService
→ Unit Test / Service Test

API Route
→ Integration Test

API Client
→ Integration/Mock Test

React Components
→ Component Test

User Journey
→ E2E Test
```

---

# 32. Folder Ownership

| Folder | Owner / Concern |
|---|---|
| `app/` | routing dan composition frontend |
| `components/ingredients` | input bahan |
| `components/recommendations` | recommendation presentation |
| `components/recipes` | detail resep |
| `components/ui` | generic UI |
| `components/showcase` | portfolio engineering presentation |
| `lib/api` | komunikasi API |
| `hooks` | frontend state/data fetching |
| `api/v1/routes` | HTTP endpoints |
| `schemas` | API contracts |
| `services` | application orchestration |
| `domain/matching` | core recommendation logic |
| `domain/models` | business entities |
| `repositories` | data access |
| `services/ai` | AI integration |
| `data/recipes` | curated dataset |
| `tests` | automated verification |

---

# 33. Aturan Penamaan

### Frontend

React component:

```text
PascalCase.tsx
```

Contoh:

```text
RecipeCard.tsx
IngredientInput.tsx
```

Hook:

```text
useCamelCase.ts
```

Contoh:

```text
useRecommendations.ts
```

Utility:

```text
camelCase.ts
```

### Backend

Python module:

```text
snake_case.py
```

Contoh:

```text
recommendation_service.py
ingredient_normalizer.py
```

Class:

```text
PascalCase
```

Function:

```text
snake_case
```

---

# 34. Anti-Patterns

Jangan membuat:

```text
components/RecipePage.tsx
```

yang berisi:

- API request;
- normalization;
- scoring;
- ranking;
- UI;
- error mapping.

Jangan membuat:

```text
routes/recommendations.py
```

yang berisi seluruh algoritma recommendation.

Jangan membuat:

```text
openai_service.py
```

yang menentukan semua business logic.

Jangan membuat folder terlalu dalam hanya untuk mematuhi pattern.

---

# 35. Contoh Good vs Bad

## Bad

```python
@router.post("/recommendations")
def recommend(request):
    recipes = load_json()

    for recipe in recipes:
        # normalize
        # calculate score
        # rank
        # build response
        ...

    return result
```

## Good

```python
@router.post("/recommendations")
def recommend(request):
    return recommendation_service.recommend(
        request.ingredients,
        request.limit
    )
```

Kemudian:

```text
RecommendationService
        ↓
Normalizer
        ↓
Repository
        ↓
MatchingEngine
        ↓
Ranking
```

---

# 36. Component Creation Checklist

Sebelum membuat komponen baru, AI Agent/developer harus bertanya:

1. Apakah komponen ini memiliki tanggung jawab yang jelas?
2. Apakah logic-nya sebenarnya milik component lain?
3. Apakah komponen ini akan digunakan ulang?
4. Apakah abstraction ini mengurangi kompleksitas atau justru menambahnya?
5. Apakah component ini mudah diuji?

Jangan membuat component hanya karena file mulai panjang.

---

# 37. Rekomendasi Urutan Pembuatan Komponen

### Backend

```text
1. Domain models
2. Ingredient normalizer
3. Scoring
4. Matching engine
5. Ranking
6. Recipe repository
7. Recommendation service
8. API schemas
9. API routes
10. AI service boundary
```

### Frontend

```text
1. UI primitives
2. API client
3. Recommendation hook
4. IngredientInput
5. RecommendationList
6. RecommendationCard
7. RecipeDetail
8. Loading / empty / error states
9. API showcase
10. Portfolio polish
```

---

# 38. Definition of Component Done

Komponen dianggap selesai ketika:

- tanggung jawabnya jelas;
- dependency-nya mengikuti architecture rules;
- tidak mengandung logic milik layer lain;
- mempunyai typing yang memadai;
- mempunyai test bila mengandung logic;
- error state ditangani bila relevan;
- tidak membuat abstraction berlebihan;
- dapat dipahami AI Agent tanpa konteks tersembunyi.

---

# 39. Panduan untuk OpenCode / AI Agent

Saat AI Agent akan membuat atau mengubah komponen:

```text
1. Baca PRD.
2. Baca technical-architecture.md.
3. Baca component-architecture.md.
4. Identifikasi layer yang bertanggung jawab.
5. Cari komponen/service yang sudah ada.
6. Reuse sebelum membuat abstraction baru.
7. Implementasikan perubahan sekecil mungkin.
8. Tambahkan/update test.
9. Jalankan lint/typecheck/test.
10. Periksa dependency boundary.
```

AI Agent tidak boleh:

- memindahkan business logic ke frontend tanpa alasan;
- memasukkan database access ke component;
- menambahkan LLM ke matching engine tanpa perubahan architecture decision;
- memperkenalkan library besar untuk kebutuhan kecil;
- mengubah folder structure secara luas tanpa kebutuhan.

---

# 40. Decision Log

### Decision 1 — Recommendation Engine sebagai domain component

**Alasan:** Recommendation adalah inti nilai produk dan harus dapat diuji secara independen.

### Decision 2 — Frontend sebagai consumer API

**Alasan:** Mendukung positioning project sebagai API-first portfolio.

### Decision 3 — AI terisolasi

**Alasan:** AI dapat berkembang tanpa mengubah deterministic core.

### Decision 4 — JSON repository untuk MVP

**Alasan:** Dataset 50–100 resep belum membutuhkan abstraction database yang kompleks.

### Decision 5 — Explicit UI states

**Alasan:** Loading, empty, error, dan success adalah bagian penting dari UX yang dapat diuji.

---

# 41. Final Component Map

```text
SMART LIVING
│
├── FRONTEND
│   │
│   ├── Pages
│   │   ├── Home
│   │   ├── Recipe Detail
│   │   └── API Showcase
│   │
│   ├── Ingredients
│   │   └── IngredientInput
│   │
│   ├── Recommendations
│   │   ├── RecommendationSection
│   │   ├── RecommendationList
│   │   ├── RecommendationCard
│   │   ├── Loading
│   │   ├── Empty
│   │   └── Error
│   │
│   ├── Recipes
│   │   ├── RecipeDetail
│   │   ├── RecipeHeader
│   │   ├── RecipeIngredientList
│   │   └── RecipeInstructionList
│   │
│   ├── API Client
│   │   └── Recommendations / Recipes / Ingredients
│   │
│   └── Hooks
│       └── useRecommendations
│
└── BACKEND
    │
    ├── API
    │   ├── Recommendations Route
    │   ├── Recipes Route
    │   ├── Ingredients Route
    │   └── Health Route
    │
    ├── Schemas
    │   ├── Request
    │   ├── Response
    │   └── Error
    │
    ├── Application
    │   └── RecommendationService
    │
    ├── Domain
    │   ├── Ingredient
    │   ├── Recipe
    │   ├── MatchResult
    │   ├── MatchingEngine
    │   ├── Scoring
    │   └── Ranking
    │
    ├── Repository
    │   └── JsonRecipeRepository
    │
    └── AI
        ├── IngredientParser
        └── OpenAI Adapter
```

---

# 42. Source of Truth

Dokumen memiliki hubungan sebagai berikut:

```text
PRD
│
│ Menentukan WHAT & WHY
▼
Technical Architecture
│
│ Menentukan HOW
▼
Component Architecture
│
│ Menentukan WHERE & RESPONSIBILITY
▼
Implementation
│
▼
Testing
│
▼
Deployment
```

Ketika terdapat konflik:

```text
PRD
→ Technical Architecture
→ Component Architecture
→ Implementation
```

Dokumen yang lebih tinggi menjadi sumber keputusan produk/arsitektur.

---

# 43. North Star Komponen

Setiap komponen harus membantu menjaga alur inti tetap sederhana:

```text
Input bahan
     ↓
Normalisasi
     ↓
Pencocokan
     ↓
Ranking
     ↓
API
     ↓
Frontend
     ↓
Keputusan memasak
```

Jangan biarkan fitur tambahan seperti AI, database, analytics, atau design system membuat alur inti menjadi sulit dipahami.
