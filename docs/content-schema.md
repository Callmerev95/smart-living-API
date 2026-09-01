# Content Schema — Smart Living API

**Versi:** 1.1
**Status:** Draf Implementasi MVP
**Dokumen Terkait:** `prd.md`, `technical-architecture.md`, `component-architecture.md`
**Tujuan Dokumen:** Menjadi sumber resmi untuk (A) struktur dataset resep & bahan, dan
(B) konten/copy yang ditampilkan frontend. Dokumen ini juga mencatat **Contract Delta v1.1**
— tiga keputusan produk yang belum tercermin di `technical-architecture.md`.

---

## 0. Cara Membaca Dokumen Ini

Dokumen ini punya dua bagian yang saling berkaitan tapi beda concern:

| Bagian | Isi | Dikonsumsi oleh |
|---|---|---|
| **A** | Skema `recipes.json`, `ingredients.json`, aturan normalisasi, aturan kurasi dataset | Backend (`domain/`, `repositories/`), data curator |
| **B** | Copy UI, pesan error/empty, mapping error code → pesan user, konten API showcase | Frontend (`components/`, `lib/constants/`) |

Bila terjadi konflik antara dokumen ini dan `technical-architecture.md` **khusus untuk
3 poin Contract Delta v1.1 (§A.9)**, dokumen ini menang. Untuk hal lain,
`technical-architecture.md` tetap lebih tinggi.

---
---

# BAGIAN A — DATASET SCHEMA

---

## A.1 Lokasi File

```text
data/recipes/
├── recipes.json        # 60 resep
└── ingredients.json    # ~120 ingredient kanonik
```

Keduanya version-controlled, di-load oleh `JsonRecipeRepository` saat startup.

---

## A.2 Skema `ingredients.json`

Kamus bahan kanonik. Sumber tunggal untuk normalisasi input user.

### A.2.1 Struktur

```json
[
  {
    "name": "egg",
    "displayName": "Telur",
    "aliases": ["eggs", "telur", "telor", "butir telur"],
    "category": "protein",
    "staple": false
  }
]
```

### A.2.2 Definisi Field

| Field | Tipe | Wajib | Aturan |
|---|---|---|---|
| `name` | `string` | ya | Canonical name. Bahasa **Inggris**, `lowercase`, `snake_case` untuk multi-kata (`soy_sauce`, `chicken_breast`). Unik di seluruh file. Immutable — jangan diubah setelah dipakai di `recipes.json`. |
| `displayName` | `string` | ya | Label tampilan bahasa **Indonesia**, Title Case (`Telur`, `Kecap Manis`). Boleh diubah tanpa breaking change. |
| `aliases` | `string[]` | ya | Varian input yang dipetakan ke `name`. `lowercase`. Boleh array kosong `[]` bila tidak ada varian. Wajib **unik lintas seluruh file** (lihat A.2.4). |
| `category` | `enum` | ya | Salah satu dari A.2.3. |
| `staple` | `boolean` | ya | `true` = bahan pokok, dikecualikan dari scoring (lihat A.9 Delta 1). |

### A.2.3 Enum `category`

| Value | Cakupan | Contoh |
|---|---|---|
| `protein` | Daging, ikan, telur, tahu, tempe | `chicken`, `egg`, `tofu`, `tempeh`, `shrimp` |
| `vegetable` | Sayur, jamur | `carrot`, `spinach`, `cabbage`, `mushroom` |
| `fruit` | Buah (termasuk yang dipakai sebagai bumbu) | `lime`, `tomato`, `tamarind` |
| `grain` | Beras, mie, tepung, roti | `rice`, `noodle`, `flour`, `bread` |
| `dairy` | Susu & turunan | `milk`, `cheese`, `butter` |
| `spice` | Rempah & bumbu aromatik | `garlic`, `shallot`, `chili`, `galangal`, `turmeric` |
| `condiment` | Saus, kecap, pasta bumbu | `soy_sauce`, `oyster_sauce`, `shrimp_paste` |
| `staple` | Bahan pokok dapur | `salt`, `cooking_oil`, `water`, `pepper`, `sugar` |
| `other` | Tidak masuk kategori di atas | `coconut_milk`, `ice_cube` |

> `category: "staple"` dan flag `staple: true` **berbeda concern**. `category` untuk
> grouping/filter UI. `staple` untuk aturan scoring. Umumnya keduanya sejalan, tapi
> flag `staple` adalah yang dipakai engine.

### A.2.4 Aturan Validasi `ingredients.json`

Wajib dipenuhi. Dicek oleh validator script (task `T-P2-03`).

1. `name` unik di seluruh file.
2. Tidak ada `alias` yang duplikat lintas ingredient. `"telur"` tidak boleh muncul di
   dua ingredient berbeda — akan membuat normalisasi ambigu.
3. Tidak ada `alias` yang sama dengan `name` ingredient **lain**.
   Contoh dilarang: ingredient `chili` punya alias `"pepper"`, sementara ada ingredient
   `pepper` terpisah.
4. `alias` yang sama dengan `name` sendiri diizinkan tapi redundan — sebaiknya dihindari.
5. Semua `aliases` harus `lowercase` dan sudah ter-trim.
6. `category` harus salah satu enum A.2.3.
7. Minimal satu ingredient dengan `staple: true` harus ada (target: 5–8).

### A.2.5 Panduan Menyusun `aliases`

Sertakan varian ini bila relevan:

| Jenis varian | Contoh untuk `egg` |
|---|---|
| Bahasa Indonesia | `telur` |
| Typo/ejaan umum | `telor` |
| Plural Inggris | `eggs` |
| Bentuk spesifik yang dinormalisasi ke umum | `chicken breast` → `chicken` |
| Frasa satuan | `butir telur` |

**Jangan** sertakan:
- Angka atau kuantitas (`2 telur`) — ditangani normalizer, bukan alias.
- Varian dengan bentuk yang secara semantik beda bahan (`egg white` ≠ `egg`
  untuk MVP; kalau memang perlu, buat ingredient terpisah).

### A.2.6 Contoh Entri Nyata (5 ingredient)

```json
[
  {
    "name": "egg",
    "displayName": "Telur",
    "aliases": ["eggs", "telur", "telor", "butir telur"],
    "category": "protein",
    "staple": false
  },
  {
    "name": "chicken",
    "displayName": "Ayam",
    "aliases": ["ayam", "chicken breast", "dada ayam", "chicken thigh", "paha ayam", "ayam fillet"],
    "category": "protein",
    "staple": false
  },
  {
    "name": "carrot",
    "displayName": "Wortel",
    "aliases": ["carrots", "wortel"],
    "category": "vegetable",
    "staple": false
  },
  {
    "name": "soy_sauce",
    "displayName": "Kecap Manis",
    "aliases": ["kecap", "kecap manis", "sweet soy sauce"],
    "category": "condiment",
    "staple": false
  },
  {
    "name": "cooking_oil",
    "displayName": "Minyak Goreng",
    "aliases": ["minyak", "minyak goreng", "oil", "vegetable oil"],
    "category": "staple",
    "staple": true
  }
]
```

---

## A.3 Skema `recipes.json`

### A.3.1 Struktur

```json
[
  {
    "id": "recipe_001",
    "name": "Omelet Ayam Wortel",
    "description": "Omelet praktis dengan ayam dan wortel, cocok untuk sarapan cepat.",
    "ingredients": [
      { "name": "egg", "required": true },
      { "name": "chicken", "required": true },
      { "name": "carrot", "required": true },
      { "name": "shallot", "required": false },
      { "name": "salt", "required": true },
      { "name": "cooking_oil", "required": true }
    ],
    "cookingTimeMinutes": 15,
    "difficulty": "easy",
    "servings": 2,
    "steps": [
      "Kocok telur, bumbui dengan garam dan lada.",
      "Potong ayam dan wortel kecil-kecil, tumis hingga ayam matang.",
      "Tuang telur kocok ke wajan, ratakan.",
      "Masak dengan api sedang hingga bagian bawah set, lipat, lalu sajikan."
    ],
    "tags": ["sarapan", "praktis", "indonesian"],
    "source": "original"
  }
]
```

### A.3.2 Definisi Field

| Field | Tipe | Wajib | Aturan |
|---|---|---|---|
| `id` | `string` | ya | Format `recipe_NNN`, zero-padded 3 digit (`recipe_001` … `recipe_060`). Unik. Immutable — dipakai sebagai tie-breaker ranking dan URL detail. |
| `name` | `string` | ya | Nama resep bahasa **Indonesia**. Title Case. Maks ~60 karakter agar tidak overflow di card. |
| `description` | `string` | ya | 1 kalimat, 60–140 karakter. Menjelaskan hasil akhir + konteks pakai, bukan mengulang daftar bahan. |
| `ingredients` | `object[]` | ya | Minimal 3 item. Struktur di A.3.3. |
| `cookingTimeMinutes` | `int` | ya | > 0, ≤ 180. Waktu total (prep + cook). Dipakai sebagai tie-breaker ranking. |
| `difficulty` | `enum` | ya | `easy` \| `medium` \| `hard`. Kriteria di A.3.4. |
| `servings` | `int` | ya | > 0. Umumnya 1–4 (produk menyasar 1–2 orang). |
| `steps` | `string[]` | ya | Minimal 3, maksimal 10 langkah. Aturan penulisan di A.3.5. |
| `tags` | `string[]` | ya | `lowercase`, 1–5 tag. Vocabulary di A.3.6. Belum dipakai matching di MVP — disiapkan untuk V1.2 personalisasi. |
| `source` | `string` | ya | MVP selalu `"original"` (resep ditulis sendiri, menghindari isu lisensi — jawaban PRD §26 Q5). |

### A.3.3 Struktur `ingredients[]`

```json
{ "name": "egg", "required": true }
```

| Field | Tipe | Wajib | Aturan |
|---|---|---|---|
| `name` | `string` | ya | **Wajib ada di `ingredients.json`** sebagai `name` kanonik. Bukan alias, bukan `displayName`. |
| `required` | `boolean` | ya | `true` = masuk denominator scoring (kecuali staple). `false` = opsional, tidak memengaruhi `matchPercentage`. |

**Field yang TIDAK ada di MVP:** `quantity`, `unit`. Kuantitas out of scope MVP
(jawaban PRD §26 Q4, direncanakan V1.1). Kuantitas ditulis di dalam `steps` sebagai
teks bila perlu.

### A.3.4 Kriteria `difficulty`

Supaya konsisten antar resep, bukan penilaian subjektif:

| Value | Kriteria |
|---|---|
| `easy` | ≤ 6 langkah, teknik dasar (tumis, kukus, rebus, goreng), tidak butuh timing presisi |
| `medium` | 7–9 langkah, atau ada teknik yang butuh perhatian (bikin bumbu halus, api bertahap, marinasi) |
| `hard` | ≥ 10 langkah, atau butuh multi-tahap/timing kritis (santan tidak boleh pecah, deep-fry bertahap) |

Untuk dataset MVP, distribusi target: **~60% easy, ~30% medium, ~10% hard**. MVP menyasar
pemula yang butuh solusi cepat.

### A.3.5 Aturan Penulisan `steps`

1. Satu langkah = satu aksi utama. Jangan gabung 4 aksi dalam satu string.
2. Kalimat imperatif bahasa Indonesia: "Tumis bawang hingga wangi."
3. Sebut kuantitas/ukuran di dalam step bila penting: "Tambahkan 100 ml air."
4. Sebut indikator selesai, bukan hanya durasi: "hingga wangi", "hingga berubah warna",
   "hingga mengental" — lebih berguna daripada "masak 3 menit" saja. Boleh keduanya.
5. Jangan menulis nomor di dalam string (`"1. Tumis..."`) — urutan berasal dari array.
6. Step terakhir sebaiknya mencakup penyajian.
7. Hindari menyebut bahan yang tidak ada di `ingredients[]`.

### A.3.6 Vocabulary `tags`

Gunakan tag dari daftar ini agar konsisten. Boleh tambah bila ada kebutuhan nyata.

| Grup | Tag |
|---|---|
| Waktu makan | `sarapan`, `makan-siang`, `makan-malam`, `camilan` |
| Karakter | `praktis`, `hemat`, `pedas`, `berkuah`, `kering`, `sehat` |
| Kuliner | `indonesian`, `chinese-indonesian`, `western-sederhana` |
| Diet (informasional, bukan klaim medis) | `vegetarian`, `no-pork`, `no-beef` |

### A.3.7 Aturan Validasi `recipes.json`

Dicek oleh validator script (task `T-P2-03`). Gagal = dataset tidak boleh di-commit.

1. `id` unik, format `recipe_NNN`.
2. **Referential integrity:** setiap `ingredients[].name` harus ada di
   `ingredients.json`. Ini aturan paling penting — pelanggaran membuat matching silent-fail.
3. Tidak ada `ingredients[].name` duplikat dalam satu resep.
4. Setiap resep punya **minimal 2 ingredient non-staple dengan `required: true`**.
   Kalau semua required-nya staple, denominator scoring jadi 0 (lihat A.9 Delta 1).
5. `len(steps) >= 3` dan `<= 10`.
6. `cookingTimeMinutes > 0` dan `<= 180`.
7. `difficulty` salah satu enum A.3.4.
8. `servings > 0`.
9. `len(tags) >= 1` dan `<= 5`.
10. `source` non-empty.

### A.3.8 Contoh Entri Nyata (2 resep)

```json
[
  {
    "id": "recipe_001",
    "name": "Omelet Ayam Wortel",
    "description": "Omelet praktis dengan ayam dan wortel, cocok untuk sarapan cepat.",
    "ingredients": [
      { "name": "egg", "required": true },
      { "name": "chicken", "required": true },
      { "name": "carrot", "required": true },
      { "name": "shallot", "required": false },
      { "name": "salt", "required": true },
      { "name": "pepper", "required": false },
      { "name": "cooking_oil", "required": true }
    ],
    "cookingTimeMinutes": 15,
    "difficulty": "easy",
    "servings": 2,
    "steps": [
      "Kocok telur dalam wadah, bumbui dengan garam dan lada.",
      "Potong ayam dan wortel kecil-kecil agar cepat matang.",
      "Panaskan minyak, tumis bawang merah hingga wangi, masukkan ayam hingga berubah warna.",
      "Masukkan wortel, tumis hingga sedikit lunak.",
      "Tuang telur kocok, ratakan, masak dengan api sedang hingga bagian bawah set.",
      "Lipat omelet, masak 1 menit lagi, lalu sajikan hangat."
    ],
    "tags": ["sarapan", "praktis", "indonesian"],
    "source": "original"
  },
  {
    "id": "recipe_002",
    "name": "Tumis Ayam Sayur Kecap",
    "description": "Tumisan ayam berbumbu kecap dengan sayuran, sekali masak langsung jadi lauk lengkap.",
    "ingredients": [
      { "name": "chicken", "required": true },
      { "name": "carrot", "required": true },
      { "name": "cabbage", "required": true },
      { "name": "garlic", "required": true },
      { "name": "soy_sauce", "required": true },
      { "name": "chili", "required": false },
      { "name": "salt", "required": true },
      { "name": "cooking_oil", "required": true },
      { "name": "water", "required": true }
    ],
    "cookingTimeMinutes": 20,
    "difficulty": "easy",
    "servings": 2,
    "steps": [
      "Potong ayam menjadi dadu kecil, cincang bawang putih.",
      "Panaskan minyak, tumis bawang putih hingga wangi.",
      "Masukkan ayam, masak hingga permukaannya berubah warna.",
      "Tambahkan kecap manis dan sedikit air, aduk hingga ayam terbalut bumbu.",
      "Masukkan wortel, masak 2 menit, lalu tambahkan kol.",
      "Bumbui dengan garam, masak hingga sayuran layu tapi masih renyah, sajikan."
    ],
    "tags": ["makan-siang", "praktis", "indonesian"],
    "source": "original"
  }
]
```

---

## A.4 Aturan Normalisasi Input

Deterministik, tanpa LLM (technical-architecture §7). Diimplementasikan di
`services/ingredient_normalizer.py`.

### A.4.1 Pipeline

```text
Raw input string
      ↓
1. Split pada koma (dan newline)
      ↓
2. Trim whitespace
      ↓
3. Lowercase
      ↓
4. Collapse whitespace ganda jadi satu spasi
      ↓
5. Strip prefix kuantitas & satuan
      ↓
6. Strip bentuk plural sederhana (fallback)
      ↓
7. Lookup: name → alias
      ↓
8a. Ketemu  → canonical name
8b. Tidak   → unknownIngredients[]
      ↓
9. Dedupe canonical (urutan kemunculan pertama dipertahankan)
```

### A.4.2 Aturan Strip Kuantitas (langkah 5)

Buang prefix numerik + satuan opsional di awal token:

```text
"2 eggs"            → "eggs"
"2 butir telur"     → "telur"
"1/2 wortel"        → "wortel"
"100 gr ayam"       → "ayam"
"3 sdm kecap"       → "kecap"
"250ml susu"        → "susu"
```

Satuan yang dikenali (buang bila muncul setelah angka):
`gr`, `gram`, `kg`, `ml`, `l`, `liter`, `sdm`, `sdt`, `buah`, `butir`, `siung`,
`lembar`, `batang`, `ekor`, `potong`, `ikat`, `bungkus`, `pcs`, `pieces`.

Angka yang dikenali: integer (`2`), desimal (`1.5`, `1,5`), pecahan (`1/2`).

**Penting:** kuantitas hanya dibuang, TIDAK disimpan (out of scope MVP).

### A.4.3 Aturan Plural (langkah 6)

Fallback ringan, hanya dipakai bila lookup langsung gagal:

```text
"carrots"  → "carrot"     (buang trailing "s")
"tomatoes" → "tomato"     (buang trailing "es" setelah o/s/x/ch/sh)
```

Prioritas tetap pada `aliases`. Plural Inggris yang penting **wajib** ditulis eksplisit
di `aliases` — jangan bergantung pada rule ini. Rule ini hanya jaring pengaman.

Bahasa Indonesia tidak punya plural sufiks, jadi tidak ada rule khusus. Reduplikasi
(`sayur-sayuran`) tidak ditangani MVP.

### A.4.4 Aturan Lookup (langkah 7)

Urutan pencarian, ambil yang pertama match:

1. Exact match ke `ingredients[].name`
2. Exact match ke salah satu `ingredients[].aliases`
3. Match setelah plural-strip (A.4.3) ke `name` atau `aliases`

Bila semua gagal → masuk `unknownIngredients[]`. **Jangan** fuzzy-match, jangan
menebak, jangan memetakan sembarangan (technical-architecture §7 "Input yang tidak
dikenali tidak boleh dipetakan secara sembarang").

Struktur lookup: build satu dict `alias → canonical_name` saat load, sehingga
normalisasi O(1) per token.

### A.4.5 Tabel Test Case Normalisasi

Wajib jadi test fixture (`T-P3-02`):

| Input | Output canonical | Catatan |
|---|---|---|
| `" telur "` | `egg` | trim + alias ID |
| `"TELUR"` | `egg` | lowercase |
| `"eggs"` | `egg` | alias plural |
| `"telor"` | `egg` | alias typo |
| `"chicken breast"` | `chicken` | alias bentuk spesifik |
| `"carrots"` | `carrot` | plural rule |
| `"2 eggs"` | `egg` | strip angka |
| `"100 gr ayam"` | `chicken` | strip angka + satuan |
| `"1/2 wortel"` | `carrot` | strip pecahan |
| `"telur,  ayam , wortel"` | `egg, chicken, carrot` | split + trim |
| `"telur, telur, eggs"` | `egg` | dedupe |
| `"kangkung"` (belum di kamus) | → `unknownIngredients` | tidak error |
| `""` | diabaikan | token kosong dibuang |
| `"telur, , ayam"` | `egg, chicken` | token kosong di tengah dibuang |

---

## A.5 Aturan Scoring (dengan Delta v1.1)

Formula dasar dari technical-architecture §8.1, **dimodifikasi** oleh Delta 1 (§A.9).

### A.5.1 Definisi Himpunan

Untuk satu resep:

```text
R  = { i in recipe.ingredients : i.required == true }
Rs = { i in R : ingredient_dict[i.name].staple == true }    # required staple
Rc = R \ Rs                                                 # required countable
U  = himpunan canonical ingredient dari user
```

### A.5.2 Formula

```text
matched      = | Rc ∩ U |
denominator  = | Rc |

matchPercentage = round( matched / denominator * 100 )    bila denominator > 0
                = 0                                       bila denominator == 0
```

`round()` = pembulatan half-up ke integer. `2/3 → 67`, `1/3 → 33`, `1/2 → 50`.

### A.5.3 Available & Missing

```text
availableIngredients = Rc ∩ U           # hanya required non-staple yang dimiliki
missingIngredients   = Rc \ U           # required non-staple yang belum dimiliki
```

Staple **tidak pernah** muncul di `missingIngredients` (Delta 1). Ingredient dengan
`required: false` juga tidak muncul di `missingIngredients` — opsional bukan kekurangan.

Urutan output kedua array: mengikuti urutan `ingredients[]` di resep (deterministik).

### A.5.4 Field `ingredients` di Response

Berbeda dari `availableIngredients`/`missingIngredients`. Ini daftar **lengkap** semua
bahan resep (required + optional + staple), untuk ditampilkan di detail resep.

Isi: array canonical name, urutan sesuai `recipes.json`.

### A.5.5 Tabel Test Case Scoring

Wajib jadi test fixture (`T-P3-04`, `T-P3-05`). Asumsi: `salt`, `cooking_oil`, `water`
adalah staple.

| # | Recipe required | User punya | matched/denom | match% | available | missing |
|---|---|---|---|---|---|---|
| 1 | egg, chicken, carrot, onion | egg, chicken, carrot | 3/4 | 75 | egg, chicken, carrot | onion |
| 2 | egg, chicken, carrot | egg, chicken, carrot | 3/3 | 100 | egg, chicken, carrot | — |
| 3 | egg, chicken, carrot | tofu | 0/3 | 0 | — | egg, chicken, carrot |
| 4 | egg, chicken, **salt**, **cooking_oil** | egg, chicken | 2/2 | 100 | egg, chicken | — |
| 5 | egg, chicken, **salt** | egg | 1/2 | 50 | egg | chicken |
| 6 | egg, chicken, carrot | egg, chicken, carrot, tofu, rice | 3/3 | 100 | egg, chicken, carrot | — |
| 7 | egg, chicken, carrot (+ onion `required:false`) | egg, chicken, carrot | 3/3 | 100 | egg, chicken, carrot | — |
| 8 | hanya staple (`salt`, `water`) | egg | 0/0 | 0 | — | — |

Case 4 & 5 memvalidasi Delta 1. Case 6 memvalidasi bahwa bahan user yang tidak terpakai
tidak menurunkan skor. Case 7 memvalidasi optional ingredient. Case 8 adalah guard
divide-by-zero — dilarang oleh validasi A.3.7 rule 4, tapi engine tetap harus aman.

---

## A.6 Aturan Ranking

Dari technical-architecture §8.5. Deterministik penuh — dua request identik wajib
menghasilkan urutan identik.

```text
sort key = (
  -matchPercentage,      # DESC
   missingCount,         # ASC
   cookingTimeMinutes,   # ASC
   recipeId              # ASC (string compare)
)
```

Setelah sort, terapkan:

1. **Filter threshold:** buang hasil dengan `matchPercentage < MIN_MATCH_THRESHOLD`
   (default `30`, configurable).
2. **Limit:** ambil `limit` teratas (default `5`, maks `10`).

Urutan operasi: **score → filter → sort → limit**. Filter sebelum limit agar limit
tidak terisi oleh hasil di bawah threshold.

### A.6.1 Tabel Test Case Ranking

Wajib jadi test fixture (`T-P3-06`):

| Skenario | Input | Ekspektasi |
|---|---|---|
| Beda match% | A=80, B=60 | A, B |
| Sama match%, beda missing | A=75 miss=1, B=75 miss=2 | A, B |
| Sama match% & missing, beda waktu | A=75 t=20, B=75 t=15 | B, A |
| Semua sama, beda id | `recipe_005`, `recipe_002` | `recipe_002`, `recipe_005` |
| Threshold | A=80, B=25, threshold=30 | hanya A |
| Limit | 8 resep lolos, limit=5 | 5 teratas |
| Kosong setelah filter | semua < 30 | `results: []`, HTTP 200 |

---

## A.7 Konfigurasi

Nilai default yang harus configurable (`core/config.py`, override via env):

| Konstanta | Default | Batas | Sumber |
|---|---|---|---|
| `DEFAULT_LIMIT` | `5` | — | PRD §8.4 |
| `MAX_LIMIT` | `10` | — | technical-architecture §9.1 |
| `MIN_MATCH_THRESHOLD` | `30` | 0–100 | PRD §8.4 |
| `MAX_INGREDIENTS_PER_REQUEST` | `30` | — | guard payload (technical-architecture §17) |
| `MAX_INGREDIENT_NAME_LENGTH` | `60` | — | guard payload |

---

## A.8 Target & Komposisi Dataset MVP

### A.8.1 Target Kuantitas

| Item | Target |
|---|---|
| Resep | **60** |
| Ingredient kanonik | **~120** |
| Staple | 5–8 |
| Rata-rata ingredient per resep | 6–9 |
| Rata-rata required non-staple per resep | 4–7 |

60 resep memenuhi minimum `technical-architecture` §21 (≥50) dan berada dalam rentang
PRD §12 (50–100), tapi tetap realistis untuk dikurasi manual dengan kualitas terjaga.

### A.8.2 Komposisi yang Disengaja

Dataset harus dirancang agar recommendation engine terlihat hidup, bukan sekadar banyak:

1. **Overlap bahan tinggi.** Bahan umum (`egg`, `chicken`, `rice`, `garlic`, `shallot`,
   `chili`, `carrot`, `tofu`, `tempeh`) harus muncul di banyak resep. Tanpa overlap,
   satu input hanya cocok ke 1 resep dan ranking jadi tidak bermakna.
2. **Gradasi match%.** Untuk input umum seperti `telur, ayam, wortel`, dataset harus
   menghasilkan sebaran skor (100%, 75%, 60%, 50%) — bukan semua 100% atau semua 0%.
   Ini yang membuat demo terasa nyata.
3. **Variasi ukuran resep.** Ada resep 3 bahan (super praktis) sampai 10 bahan
   (lebih kompleks). Resep kecil memberi peluang match 100%.
4. **Variasi waktu.** Sebar `cookingTimeMinutes` agar tie-breaker waktu benar-benar
   terpakai.

### A.8.3 Distribusi Target

| Dimensi | Target |
|---|---|
| `difficulty` | ~60% easy, ~30% medium, ~10% hard |
| Protein utama | ayam ~15, telur ~10, tahu/tempe ~10, ikan/seafood ~8, daging ~5, sayur-only ~12 |
| `cookingTimeMinutes` | ~40% ≤15 menit, ~40% 16–30, ~20% >30 |
| Kuliner | mayoritas `indonesian`, sisanya chinese-indonesian & western sederhana |

### A.8.4 Strategi Kurasi

Tulis dataset bertahap, bukan 60 resep sekaligus:

```text
Batch 1: 15 resep — bahan paling umum (telur, ayam, tahu, tempe, nasi, sayur dasar)
Batch 2: 15 resep — perluas protein & sayur
Batch 3: 15 resep — variasi kuliner & difficulty
Batch 4: 15 resep — isi celah kombinasi yang belum tercakup
```

Setiap batch: jalankan validator (A.3.7) + commit terpisah. Ingredient baru
ditambahkan ke `ingredients.json` **sebelum** dipakai di resep.

### A.8.5 Aturan Anti-Karang

- Resep harus masuk akal secara kuliner dan bisa benar-benar dimasak.
- `source: "original"` — tulis sendiri, jangan copy dari situs resep (isu lisensi,
  PRD §26 Q5).
- Jangan menambah resep di luar dokumen ini tanpa memperbarui `ingredients.json`.
- Jangan mengklaim nilai nutrisi (PRD §5 non-goal).

---

## A.9 Contract Delta v1.1

Tiga keputusan produk yang **belum tercermin** di `technical-architecture.md`.
Dokumen ini adalah sumber resmi untuk ketiganya. Implementasi wajib mengikuti bagian ini.

---

### Delta 1 — Staples Dikecualikan dari Scoring

**Menjawab:** PRD §26 Q1.

**Keputusan:** Ingredient dengan `staple: true` dianggap selalu tersedia di dapur user.

**Konsekuensi:**
- Tidak masuk `missingIngredients`.
- Tidak masuk denominator `matchPercentage`.
- Tidak masuk `availableIngredients` (tidak perlu dilaporkan sebagai "punya").
- **Tetap** muncul di field `ingredients` (daftar lengkap) agar user tahu resep butuh minyak.

**Alasan:** Tanpa aturan ini, resep dengan `salt` + `cooking_oil` + `water` sebagai
required akan selalu kehilangan 3 poin meski user punya semua bahan utama —
match% turun tanpa alasan yang bermakna bagi user. Contoh: user punya telur+ayam,
resep butuh telur+ayam+garam+minyak → 2/4 = 50% (menyesatkan) vs 2/2 = 100% (benar).

**Kandidat staple:** `salt`, `cooking_oil`, `water`, `pepper`, `sugar`.

**Konflik dengan dok existing:** `technical-architecture.md` §8.1 mendefinisikan
denominator sebagai `totalRequiredIngredients` tanpa pengecualian. Gunakan §A.5.2.

---

### Delta 2 — `unknownIngredients[]` di Response

**Keputusan:** Bahan di luar kamus dikembalikan dalam `unknownIngredients[]` dengan
**HTTP 200**, bukan error.

**Konsekuensi:**
- Response `POST /api/v1/recommendations` punya field baru `unknownIngredients: string[]`.
- Berisi input asli setelah normalisasi ringan (lowercase + trim), bukan canonical
  (karena tidak ada canonical-nya).
- Bahan unknown **tidak** dipakai matching.
- Error code `INGREDIENT_NOT_FOUND` **tidak** dipakai untuk kasus ini di endpoint
  recommendations. (Masih valid untuk `GET /api/v1/ingredients/{name}` bila kelak ada.)
- Bila **semua** input unknown → `results: []` + `unknownIngredients` terisi, tetap 200.
  Frontend tampilkan empty state yang menjelaskan penyebabnya.

**Alasan:** Kamus 120 bahan pasti tidak lengkap. Menolak seluruh request karena satu
bahan tak dikenal merusak UX — user kehilangan rekomendasi untuk bahan lain yang valid.
Transparansi lebih baik daripada silent-drop: user tahu `kangkung` belum didukung.

**Tidak pakai fuzzy match** di MVP: menjaga determinisme dan menghindari salah petakan
(technical-architecture §7).

**Konflik dengan dok existing:** contoh response `technical-architecture.md` §9.1
belum punya field ini.

---

### Delta 3 — Normalisasi Transparan

**Keputusan:** Response membawa hasil normalisasi agar frontend bisa menampilkan
mapping input → canonical.

**Konsekuensi:**
- `query.ingredients` berisi **canonical** name hasil normalisasi (`["egg","chicken"]`),
  bukan echo input mentah.
- `query.raw` berisi input asli user untuk perbandingan.
- Frontend menampilkan chip `telur → Telur (egg)` sehingga user paham sistem mengerti
  inputnya.

**Alasan:** PRD §15 prinsip UX #3 "Transparan: tunjukkan alasan sebuah resep memperoleh
skor kecocokan tertentu". User tidak bisa mempercayai skor kalau tidak tahu bahan apa
yang sebenarnya dipakai sistem. Ini juga memudahkan debugging normalisasi saat demo.

**Konflik dengan dok existing:** `technical-architecture.md` §9.1 punya
`query.ingredients` tapi tidak eksplisit menyatakan itu hasil normalisasi, dan tidak
punya `query.raw`.

---

## A.10 Contract Response Final (v1.1)

Menggabungkan technical-architecture §9 dengan Delta v1.1.

### A.10.1 `POST /api/v1/recommendations`

**Request:**

```json
{
  "ingredients": ["telur", "ayam", "wortel", "kangkung"],
  "limit": 5
}
```

Validasi request:

| Aturan | Error |
|---|---|
| `ingredients` wajib ada | `VALIDATION_ERROR` (422) |
| `ingredients` minimal 1 item non-empty | `INVALID_INGREDIENTS` (400) |
| `ingredients` maks 30 item | `INVALID_INGREDIENTS` (400) |
| Tiap item maks 60 karakter | `INVALID_INGREDIENTS` (400) |
| `limit` opsional, default 5 | — |
| `limit` antara 1 dan 10 | `VALIDATION_ERROR` (422) |

**Response 200:**

```json
{
  "query": {
    "raw": ["telur", "ayam", "wortel", "kangkung"],
    "ingredients": ["egg", "chicken", "carrot"]
  },
  "unknownIngredients": ["kangkung"],
  "results": [
    {
      "id": "recipe_001",
      "name": "Omelet Ayam Wortel",
      "description": "Omelet praktis dengan ayam dan wortel, cocok untuk sarapan cepat.",
      "matchPercentage": 100,
      "availableIngredients": ["egg", "chicken", "carrot"],
      "missingIngredients": [],
      "cookingTimeMinutes": 15,
      "difficulty": "easy",
      "servings": 2,
      "ingredients": ["egg", "chicken", "carrot", "shallot", "salt", "pepper", "cooking_oil"],
      "steps": [
        "Kocok telur dalam wadah, bumbui dengan garam dan lada.",
        "Potong ayam dan wortel kecil-kecil agar cepat matang."
      ],
      "tags": ["sarapan", "praktis", "indonesian"]
    }
  ],
  "meta": {
    "count": 1,
    "limit": 5,
    "threshold": 30
  }
}
```

Catatan field:
- `query.raw` — input asli (Delta 3).
- `query.ingredients` — canonical hasil normalisasi, sudah dedupe (Delta 3).
- `unknownIngredients` — array, `[]` bila semua dikenali (Delta 2).
- `matchPercentage` — integer 0–100, staple sudah dikecualikan (Delta 1).
- `meta.count` — jumlah item di `results` (setelah filter & limit).
- `meta.threshold` — threshold yang dipakai, untuk transparansi.

### A.10.2 `GET /api/v1/recipes/{id}`

**Response 200:** objek resep penuh (semua field A.3.2, canonical name apa adanya).
Tanpa `matchPercentage`/`availableIngredients`/`missingIngredients` — field itu hanya
bermakna dalam konteks query rekomendasi.

**Response 404:** `RECIPE_NOT_FOUND`.

### A.10.3 `GET /api/v1/ingredients`

**Response 200:**

```json
{
  "ingredients": [
    {
      "name": "egg",
      "displayName": "Telur",
      "aliases": ["eggs", "telur", "telor", "butir telur"],
      "category": "protein",
      "staple": false
    }
  ],
  "meta": { "count": 120 }
}
```

Dipakai frontend untuk autocomplete (V1.1) dan API showcase.

### A.10.4 `GET /api/v1/health`

```json
{ "status": "ok", "recipeCount": 60, "ingredientCount": 120 }
```

`recipeCount`/`ingredientCount` membuktikan dataset benar-benar ter-load — lebih
berguna daripada `{"status":"ok"}` polos.

### A.10.5 Error Response

Format konsisten (technical-architecture §10):

```json
{
  "error": {
    "code": "INVALID_INGREDIENTS",
    "message": "Bahan harus berisi setidaknya satu item.",
    "details": null
  }
}
```

| Code | HTTP | Kapan |
|---|---|---|
| `INVALID_INGREDIENTS` | 400 | `ingredients` kosong / melebihi batas |
| `VALIDATION_ERROR` | 422 | Pydantic validation gagal (tipe salah, limit di luar rentang) |
| `RECIPE_NOT_FOUND` | 404 | `GET /recipes/{id}` id tidak ada |
| `INGREDIENT_NOT_FOUND` | 404 | Reserved — belum dipakai MVP (lihat Delta 2) |
| `INTERNAL_ERROR` | 500 | Unhandled exception. **Jangan** kirim stack trace |

---
---

# BAGIAN B — UI CONTENT SCHEMA

Copy dan konten frontend. Disimpan terpusat di `apps/web/lib/constants/content.ts`
agar tidak tersebar sebagai string literal di banyak component, dan siap untuk i18n
bila kelak dibutuhkan.

---

## B.1 Prinsip Penulisan Copy

1. **Bahasa Indonesia**, sapaan informal-sopan (`kamu`, bukan `Anda` — target user
   mahasiswa/young adult per PRD §6).
2. **Tanpa jargon teknis** di area user. `matchPercentage` ditampilkan sebagai
   "cocok", bukan "match percentage". Jargon hanya di API showcase.
3. **Actionable.** Setiap empty/error state menyebut langkah berikutnya, bukan cuma
   menyatakan masalah.
4. **Jangan menyalahkan user.** "Bahan belum dikenali" bukan "Input kamu salah".
5. **Ringkas.** Heading ≤ 8 kata, body ≤ 2 kalimat.
6. Tanpa emoji (kecuali diminta eksplisit).

---

## B.2 Hero Section

| Key | Konten |
|---|---|
| `hero.title` | Apa yang bisa saya masak dari bahan yang sudah ada? |
| `hero.subtitle` | Masukkan bahan yang ada di kulkas, dapatkan ide masakan yang benar-benar bisa kamu buat hari ini. |
| `hero.badge` | API-first · Deterministic matching |

`hero.title` diambil langsung dari PRD §8.6.

---

## B.3 Ingredient Input

| Key | Konten |
|---|---|
| `input.label` | Bahan yang kamu punya |
| `input.placeholder` | telur, ayam, wortel |
| `input.helper` | Pisahkan dengan koma. Boleh bahasa Indonesia atau Inggris. |
| `input.submit` | Cari Resep |
| `input.submitLoading` | Mencari… |
| `input.clear` | Hapus semua |
| `input.exampleLabel` | Coba contoh: |
| `input.examples` | `["telur, ayam, wortel", "tahu, tempe, kecap", "nasi, telur, bawang putih"]` |

Contoh input harus benar-benar menghasilkan ≥3 resep pada dataset final —
jadi bagian ini divalidasi ulang setelah dataset selesai (task `T-P5-11`).

---

## B.4 Chip Bahan (Normalisasi Transparan — Delta 3)

Menampilkan hasil normalisasi.

| Kondisi | Tampilan | Key |
|---|---|---|
| Dikenali & berubah | `telur → Telur` | `chip.normalized` |
| Dikenali & sama | `Telur` | `chip.plain` |
| Tidak dikenali | `kangkung · tidak dikenali` | `chip.unknown` |

| Key | Konten |
|---|---|
| `chip.unknownSuffix` | tidak dikenali |
| `chip.unknownTooltip` | Bahan ini belum ada di kamus kami, jadi tidak dipakai saat mencari resep. |
| `chip.normalizedTooltip` | Kami mengenali bahan ini sebagai {displayName}. |

---

## B.5 State Rekomendasi

Empat state eksplisit (component-architecture §30).

### B.5.1 Initial

| Key | Konten |
|---|---|
| `results.initial.title` | Mulai dari bahan yang ada |
| `results.initial.body` | Masukkan minimal satu bahan, lalu kami tunjukkan masakan yang paling mungkin kamu buat. |

### B.5.2 Loading

| Key | Konten |
|---|---|
| `results.loading.label` | Mencocokkan bahan dengan resep… |

Tampilkan 3 skeleton card (`RecommendationSkeleton`).

### B.5.3 Success

| Key | Konten |
|---|---|
| `results.success.heading` | {count} resep cocok untuk bahanmu |
| `results.success.headingSingle` | 1 resep cocok untuk bahanmu |
| `results.success.sortNote` | Diurutkan dari yang paling cocok. |

### B.5.4 Empty — Tidak Ada Resep Cocok

| Key | Konten |
|---|---|
| `results.empty.title` | Belum ada resep yang cukup cocok |
| `results.empty.body` | Kami tidak menemukan kecocokan yang kuat. Coba tambah satu atau dua bahan lagi. |
| `results.empty.cta` | Tambah bahan |

Diadaptasi dari PRD §16.

### B.5.5 Empty — Semua Bahan Tidak Dikenali (Delta 2)

Varian khusus, lebih informatif daripada empty biasa:

| Key | Konten |
|---|---|
| `results.allUnknown.title` | Bahan belum ada di kamus kami |
| `results.allUnknown.body` | Kami belum mengenali {list}. Coba tulis dengan nama yang lebih umum, misalnya "telur" atau "ayam". |

### B.5.6 Error

| Key | Konten |
|---|---|
| `results.error.title` | Gagal mengambil rekomendasi |
| `results.error.body` | Terjadi masalah saat menghubungi server. Coba lagi sebentar. |
| `results.error.retry` | Coba lagi |

---

## B.6 Recommendation Card

| Key | Konten |
|---|---|
| `card.matchLabel` | {percentage}% cocok |
| `card.availableLabel` | Sudah ada |
| `card.missingLabel` | Perlu dibeli |
| `card.missingEmpty` | Semua bahan utama sudah ada |
| `card.timeLabel` | {minutes} menit |
| `card.servingsLabel` | {servings} porsi |
| `card.cta` | Lihat Resep |

### B.6.1 Label `difficulty`

| Value | Label |
|---|---|
| `easy` | Mudah |
| `medium` | Sedang |
| `hard` | Sulit |

### B.6.2 Tier Visual `matchPercentage`

Untuk warna badge — mendukung PRD §16 "tampilkan kecocokan rendah secara jelas
daripada menyembunyikannya":

| Rentang | Tier | Maksud visual |
|---|---|---|
| 100 | `perfect` | Semua bahan utama ada |
| 70–99 | `high` | Sangat mungkin dibuat |
| 50–69 | `medium` | Perlu beberapa bahan |
| 30–49 | `low` | Perlu banyak bahan |

Di bawah 30 tidak muncul (difilter threshold).

| Key | Konten |
|---|---|
| `card.tier.perfect` | Semua bahan utama ada |
| `card.tier.high` | Hampir lengkap |
| `card.tier.medium` | Perlu beberapa bahan |
| `card.tier.low` | Perlu banyak bahan |

---

## B.7 Recipe Detail

| Key | Konten |
|---|---|
| `detail.ingredientsHeading` | Bahan |
| `detail.stepsHeading` | Cara Membuat |
| `detail.metaHeading` | Informasi |
| `detail.stapleNote` | Bahan pokok seperti garam dan minyak dianggap sudah tersedia. |
| `detail.optionalSuffix` | (opsional) |
| `detail.back` | Kembali ke hasil |
| `detail.notFound.title` | Resep tidak ditemukan |
| `detail.notFound.body` | Resep yang kamu cari tidak ada atau sudah dihapus. |

`detail.stapleNote` penting untuk transparansi Delta 1 — user harus paham kenapa
garam tidak dihitung sebagai bahan yang kurang.

---

## B.8 Mapping Error Code → Pesan User

Frontend **tidak** menampilkan `error.message` dari API secara mentah (bisa berubah,
bisa terlalu teknis). Gunakan mapping ini; `error.code` adalah kontrak yang stabil.

| `error.code` | Pesan user |
|---|---|
| `INVALID_INGREDIENTS` | Tambahkan setidaknya satu bahan untuk mencari resep. |
| `VALIDATION_ERROR` | Ada input yang belum sesuai. Periksa kembali bahan yang kamu masukkan. |
| `RECIPE_NOT_FOUND` | Resep tidak ditemukan. |
| `INGREDIENT_NOT_FOUND` | Bahan tidak ditemukan. |
| `INTERNAL_ERROR` | Ada masalah di sisi kami. Coba lagi sebentar. |
| _network failure / timeout_ | Tidak bisa menghubungi server. Periksa koneksi kamu. |
| _unknown code_ | Terjadi kesalahan. Coba lagi. |

Pesan `INVALID_INGREDIENTS` diambil dari PRD §16.

---

## B.9 Validasi UI (Client-side)

Cek ringan sebelum request, untuk feedback instan. Server tetap memvalidasi ulang —
client-side validation bukan pengganti server-side.

| Kondisi | Pesan | Aksi |
|---|---|---|
| Input kosong | Tambahkan setidaknya satu bahan untuk mencari resep. | Blok submit |
| > 30 bahan | Maksimal 30 bahan per pencarian. | Blok submit |
| Satu bahan > 60 karakter | Nama bahan terlalu panjang. | Blok submit |

---

## B.10 Konten API Showcase

Area portfolio (PRD §8.6, component-architecture §10). Ini satu-satunya area yang
boleh pakai bahasa teknis.

| Key | Konten |
|---|---|
| `showcase.heading` | Di balik layar |
| `showcase.subheading` | Frontend ini hanya salah satu client dari Smart Living API. |
| `showcase.requestHeading` | Contoh Request |
| `showcase.responseHeading` | Contoh Response |
| `showcase.architectureHeading` | Arsitektur |
| `showcase.stackHeading` | Tech Stack |
| `showcase.docsLabel` | Buka dokumentasi OpenAPI |
| `showcase.copyLabel` | Copy |
| `showcase.copiedLabel` | Tersalin |

### B.10.1 Contoh Request yang Ditampilkan

```http
POST /api/v1/recommendations
Content-Type: application/json

{
  "ingredients": ["telur", "ayam", "wortel"],
  "limit": 5
}
```

### B.10.2 Contoh Response yang Ditampilkan

Response nyata dari A.10.1 (dipangkas 1 item + `steps` dipotong agar enak dibaca).

**Aturan:** contoh ini harus **selalu** cocok dengan response API sebenarnya. Kalau
kontrak berubah, contoh ini wajib diperbarui. Mitigasi contract drift
(technical-architecture §28): idealnya contoh di-generate dari integration test
fixture, bukan ditulis manual dua kali.

### B.10.3 Diagram Arsitektur

```text
Browser
   ↓
Next.js (Web)
   ↓  HTTP / JSON
Smart Living API (FastAPI)
   ↓
Ingredient Normalizer → Matching Engine → Ranking
   ↓
Recipe Repository → recipes.json
```

### B.10.4 Tech Stack yang Ditampilkan

| Layer | Isi |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| Data | JSON (version-controlled), PostgreSQL-ready |
| Testing | pytest, Vitest, Playwright |
| Tooling | uv, pnpm, ruff, GitHub Actions |

### B.10.5 Catatan Keputusan Teknis

Konten singkat yang menjelaskan trade-off (PRD §17 metrik portfolio):

| Key | Konten |
|---|---|
| `showcase.decisions.deterministic.title` | Kenapa deterministik, bukan LLM? |
| `showcase.decisions.deterministic.body` | Ranking resep harus konsisten, murah, dan bisa dijelaskan. Input yang sama selalu menghasilkan urutan yang sama. AI ditempatkan sebagai lapisan enhancement, bukan fondasi. |
| `showcase.decisions.staple.title` | Kenapa garam dan minyak tidak dihitung? | 
| `showcase.decisions.staple.body` | Bahan pokok dapur dianggap selalu tersedia, sehingga persentase kecocokan mencerminkan bahan yang benar-benar menentukan. |
| `showcase.decisions.json.title` | Kenapa JSON, bukan database? |
| `showcase.decisions.json.body` | Untuk 60 resep, JSON version-controlled lebih cepat di-review dan tidak butuh setup. Repository abstraction membuat migrasi ke PostgreSQL tidak mengubah business logic. |

---

## B.11 Metadata & SEO

| Key | Konten |
|---|---|
| `meta.title` | Smart Living — Masak dari bahan yang sudah ada |
| `meta.description` | Masukkan bahan yang ada di kulkas, dapatkan rekomendasi masakan yang bisa langsung kamu buat. API-first, deterministic matching. |
| `meta.ogTitle` | Smart Living API |
| `footer.tagline` | Mengubah bahan sisa menjadi keputusan memasak. |
| `footer.repoLabel` | Lihat di GitHub |

`footer.tagline` diambil dari visi produk PRD §3.

---

## B.12 Aturan Placeholder

Placeholder pakai kurung kurawal, di-interpolasi di component:

```text
{count}       jumlah hasil
{percentage}  match percentage
{minutes}     cooking time
{servings}    jumlah porsi
{displayName} display name ingredient
{list}        daftar item, digabung dengan koma
```

Jangan concat string manual di JSX untuk kalimat penuh — pakai template dari
`content.ts` agar copy bisa diubah di satu tempat.

---

## B.13 Aturan Angka & Format

| Item | Format | Contoh |
|---|---|---|
| Persentase | Integer, tanpa desimal | `75% cocok` |
| Waktu | Integer menit | `15 menit` |
| Waktu ≥ 60 | Tetap menit (konsisten & mudah dibanding) | `90 menit` |
| Porsi | Integer | `2 porsi` |
| Daftar bahan di prosa | Koma, tanpa "dan" | `telur, ayam, wortel` |

---
---

# C. Traceability

Pemetaan keputusan di dokumen ini ke sumbernya.

| Keputusan | Sumber |
|---|---|
| Formula match percentage | PRD §8.3, technical-architecture §8.1 |
| Threshold 30%, limit 5, maks 10 | PRD §8.4, technical-architecture §9.1 |
| Urutan ranking + tie-breaker | technical-architecture §8.5 |
| Pipeline normalisasi | technical-architecture §7 |
| Struktur ingredient & recipe | technical-architecture §6 |
| Error code & format | technical-architecture §10 |
| Empty/error copy | PRD §16 |
| Prinsip UX (transparan) | PRD §15 |
| Ukuran dataset 50–100 | PRD §12 → dipilih 60 |
| Staple dikecualikan | **Keputusan baru** — Delta 1, menjawab PRD §26 Q1 |
| Bobot bahan rata | **Keputusan baru** — menjawab PRD §26 Q2 |
| `unknownIngredients[]` | **Keputusan baru** — Delta 2 |
| `query.raw` + normalisasi transparan | **Keputusan baru** — Delta 3 |
| Kuantitas out of scope | PRD §26 Q4 → V1.1 |
| `source: "original"` | PRD §26 Q5 |

---

# D. Changelog

| Versi | Perubahan |
|---|---|
| 1.0 | Skema awal turunan langsung dari technical-architecture §6–§10 |
| 1.1 | Delta 1 (staples dikecualikan scoring), Delta 2 (`unknownIngredients[]`), Delta 3 (normalisasi transparan + `query.raw`). Target dataset dipatok 60 resep / ~120 ingredient. Ditambah Bagian B (UI content schema). |
