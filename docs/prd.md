# PRD — Smart Living API

**Versi:** 1.0  
**Status:** Draf / Cakupan MVP  
**Tipe Produk:** Platform Smart Living berbasis API + Frontend Demo Interaktif  
**Posisi Utama dalam Portfolio:** Product Manager + Backend/API Developer + Full-stack teknologi Developer + Pengembang produk dengan AI

---

## 1. Gambaran Produk

**Smart Living API** adalah aplikasi berbasis API yang membantu pengguna mengubah bahan makanan sisa di kulkas menjadi ide masakan yang praktis.

Pengguna memasukkan bahan makanan yang mereka miliki secara manual, misalnya:

> telur, ayam, wortel

Sistem mencocokkan bahan tersebut dengan dataset resep lalu mengembalikan daftar rekomendasi resep yang telah diurutkan berdasarkan relevansi.

Setiap rekomendasi harus menampilkan:

- Persentase kecocokan
- Bahan yang sudah tersedia
- Bahan yang masih dibutuhkan
- Estimasi waktu memasak
- Tingkat kesulitan
- Langkah memasak

Produk ini sengaja dirancang sebagai:

1. Pengalaman yang berguna bagi pengguna untuk mengurangi food waste dan pengeluaran makanan.
2. Proyek portfolio yang menunjukkan kemampuan product management, engineering API/backend, pengembangan full-stack teknologi, serta lapisan AI yang terbatas tetapi bermakna.

Versi mendatang dapat mendukung deteksi bahan makanan berbasis gambar dari foto kulkas atau makanan yang diunggah.

---

## 2. Pernyataan Masalah

Orang sering memiliki bahan makanan sisa tetapi tidak tahu harus memasak apa. Hal ini menimbulkan tiga masalah terkait:

- Bahan makanan dapat kedaluwarsa sebelum digunakan.
- Pengguna mengeluarkan lebih banyak uang untuk membeli makanan karena tidak mengetahui masakan praktis dari bahan yang sudah tersedia.
- Pengguna menghabiskan waktu yang tidak perlu untuk mencari resep secara manual.

Produk harus mengurangi jarak antara **"apa yang saya punya"** dan **"apa yang bisa saya masak"**.

---

## 3. Visi Produk

> **Mengubah bahan makanan sisa menjadi keputusan memasak yang berguna.**

Smart Living harus menjadi decision engine ringan yang menjawab:

> "Dengan bahan yang sudah saya miliki, masakan realistis apa yang bisa saya buat hari ini?"

---

## 4. Tujuan Produk

### Tujuan Utama

1. Membantu pengguna menemukan resep dari bahan yang sudah mereka miliki.
2. Mendorong pengguna menggunakan bahan makanan sisa daripada membuangnya.
3. Mengurangi pengeluaran belanja/makanan yang tidak perlu dengan memaksimalkan bahan yang sudah tersedia.
4. Menyediakan API yang sederhana dan cepat yang dapat digunakan oleh berbagai client.
5. Menyediakan frontend demo interaktif yang memperlihatkan penggunaan API secara nyata.
6. Menunjukkan pemikiran produk dan eksekusi teknis yang kuat melalui proyek portfolio.

### Tujuan Sekunder

1. Menyiapkan arsitektur yang nantinya dapat mendukung input bahan berbasis gambar.
2. Membuat fondasi yang rapi untuk kemampuan AI di masa depan.
3. Mengumpulkan analitik produk anonim yang berguna untuk prioritas pengembangan berikutnya.

---

## 5. Hal yang Tidak Menjadi Target MVP

MVP **tidak** akan mencakup:

- Mendeteksi bahan makanan dari gambar.
- Melacak tanggal kedaluwarsa makanan secara akurat.
- Melakukan pengiriman atau pembelian bahan makanan.
- Membangun jejaring sosial/komunitas.
- Menghasilkan resep yang sepenuhnya baru dari LLM untuk setiap request.
- Memberikan saran medis/nutrisi.
- Menjamin nilai nutrisi yang akurat kecuali dataset resep secara eksplisit memiliki data yang telah tervalidasi.

Hal-hal tersebut dapat menjadi peluang pada roadmap masa depan.

---

## 6. Target Pengguna

### Audiens Utama

**Siapa saja yang ingin mengurangi food waste**, terutama orang yang sering memiliki sedikit bahan makanan sisa di rumah.

Contoh potensial:

- Mahasiswa / dewasa muda
- Profesional yang sibuk
- Orang yang memasak untuk satu atau dua orang
- Rumah tangga yang sadar anggaran
- Pemula yang memasak di rumah

### Karakteristik Pengguna

Secara umum, pengguna:

- Mengetahui bahan makanan yang mereka miliki.
- Menginginkan jawaban cepat daripada menelusuri puluhan resep.
- Lebih mementingkan kepraktisan daripada kompleksitas memasak.
- Lebih memilih menggunakan bahan yang sudah tersedia sebelum membeli bahan baru.

---

## 7. Alur Utama Pengguna

### Alur MVP

1. Pengguna membuka Smart Living.
2. Pengguna memasukkan bahan secara manual.
3. Frontend mengirimkan bahan ke Smart Living API.
4. API menormalisasi input bahan.
5. Mesin pencocokan membandingkan bahan pengguna dengan dataset resep.
6. Resep diberi skor dan diurutkan berdasarkan ranking.
7. API mengembalikan 5 rekomendasi teratas.
8. Frontend menampilkan kartu resep.
9. Pengguna membuka resep untuk melihat detail lengkap.

### Contoh Input

```text
 telur, ayam, wortel
```

### Contoh Konsep Output

```text
1. Chicken Carrot Omelette
   Match: 80%
   Available: egg, chicken, carrot
   Missing: onion
   Time: 15 min
   Tingkat kesulitan: Mudah

2. Chicken Vegetable Stir Fry
   Match: 75%
   Available: chicken, carrot
   Missing: broccoli, soy sauce
   Time: 20 min
   Tingkat kesulitan: Mudah
```

---

## 8. Cakupan Fitur MVP

### 8.1 Input Bahan

Pengguna dapat memasukkan bahan secara manual melalui teks bebas.

Examples:

- `telur, ayam, wortel`
- `egg, chicken, carrot`
- `2 eggs, chicken breast, carrots`

Sistem harus dapat menangani variasi sederhana pada huruf besar-kecil, spasi, serta bentuk tunggal/jamak.

### 8.2 Normalisasi Bahan

Mengubah input pengguna menjadi token bahan yang telah dinormalisasi.

Examples:

```text
" telur " -> "egg"
"eggs" -> "egg"
"chicken breast" -> "chicken"
```

Untuk MVP, normalisasi harus dibuat sederhana dan transparan.

### 8.3 Mesin Pencocokan Resep

Sistem inti membandingkan bahan pengguna yang telah dinormalisasi dengan bahan pada resep.

Setiap resep memperoleh skor kecocokan berdasarkan irisan bahan.

Pendekatan scoring MVP yang disarankan:

```text
match_percentage = matched_required_ingredients / total_required_ingredients * 100
```

Sebuah resep dapat memperoleh bonus kecil pada ranking ketika:

- Lebih banyak bahan prioritas tinggi berhasil dicocokkan.
- Lebih sedikit bahan yang hilang.
- Resep tersebut sangat praktis untuk kombinasi bahan yang dimasukkan.

Aturan penilaian harus tetap deterministik dan dapat dijelaskan.

### 8.4 5 Rekomendasi Teratas

Kembalikan lima resep dengan ranking tertinggi yang memenuhi ambang relevansi minimum.

Nilai default yang disarankan:

- Jumlah hasil maksimum: 5
- Ambang relevansi minimum: 30%

Nilai ini harus dapat dikonfigurasi.

### 8.5 Detail Resep

Setiap rekomendasi harus menyediakan:

- Nama resep
- Deskripsi singkat
- Persentase kecocokan
- Bahan yang tersedia
- Bahan yang kurang
- Daftar bahan lengkap
- Estimasi waktu memasak
- Tingkat kesulitan
- Instruksi langkah demi langkah

### 8.6 Frontend Demo Interaktif

Frontend harus secara visual mendemonstrasikan API, bukan mencoba menjadi aplikasi konsumen yang besar.

Antarmuka yang direkomendasikan:

**Hero:**
> "Apa yang bisa saya masak dari bahan yang sudah saya punya?"

**Input bahan:**
```text
[ egg, chicken, carrot                  ] [Find Recipes]
```

**Hasil:**
Lima kartu resep dengan persentase kecocokan dan detail praktis.

**Area showcase untuk developer:**
Bagian ringkas yang menampilkan:

- Endpoint API
- Contoh request
- Contoh respons JSON
- Diagram arsitektur dasar

Ini membantu proyek menunjukkan kemampuan product dan engineering secara bersamaan.

---

## 9. Kebutuhan API

### 9.1 Endpoint yang Direkomendasikan

```http
POST /api/v1/recommendations
```

### Request

```json
{
  "ingredients": ["egg", "chicken", "carrot"],
  "limit": 5
}
```

### Response

```json
{
  "query": {
    "ingredients": ["egg", "chicken", "carrot"]
  },
  "results": [
    {
      "id": "recipe_001",
      "name": "Chicken Carrot Omelette",
      "matchPercentage": 80,
      "availableIngredients": ["egg", "chicken", "carrot"],
      "missingIngredients": ["onion"],
      "cookingTimeMinutes": 15,
      "difficulty": "easy",
      "ingredients": [
        "egg",
        "chicken",
        "carrot",
        "onion"
      ],
      "steps": [
        "Prepare the ingredients.",
        "Masak ayam dan sayuran.",
        "Tambahkan telur.",
        "Masak hingga matang lalu sajikan."
      ]
    }
  ]
}
```

### 9.2 Endpoint Pendukung Opsional

```http
GET /api/v1/recipes/{id}
GET /api/v1/ingredients
GET /api/v1/health
```

Endpoint potensial di masa depan:

```http
POST /api/v1/ingredients/from-image
POST /api/v1/recipes/generate
POST /api/v1/preferences
```

Ini **bukan persyaratan MVP**.

---

## 10. Perbandingan Pencocokan Deterministik vs AI

### 10.1 Apa itu pencocokan deterministik?

Sistem deterministik mengikuti aturan yang eksplisit. Dengan input dan dataset resep yang sama, sistem seharusnya menghasilkan hasil yang sama.

Sebagai contoh:

```text
User ingredients:
Egg + Chicken + Carrot

Recipe requirements:
Egg + Chicken + Carrot + Onion

Matched = 3
Required = 4

Match = 3 / 4 = 75%
```

Pendekatan ini dapat diprediksi, murah, cepat, mudah diuji, dan mudah dijelaskan kepada pengguna.

### 10.2 Apa yang berubah jika menggunakan LLM seperti OpenAI API?

LLM dapat memahami bahasa yang lebih fleksibel serta menghasilkan atau mentransformasikan konten.

Sebagai contoh, pengguna dapat memasukkan:

> "Saya punya dua telur, sisa ayam panggang, dan setengah wortel."

LLM dapat memahami input bahasa natural yang tidak terstruktur tersebut dan berpotensi memberikan rekomendasi resep dengan cara yang lebih fleksibel dan kreatif.

AI juga dapat:

- Menormalisasi deskripsi bahan yang tidak umum.
- Menyarankan substitusi bahan.
- Menjelaskan mengapa sebuah resep cocok.
- Menghasilkan variasi resep.
- Membuat asisten memasak berbasis percakapan.

Namun, LLM kurang dapat diprediksi dibandingkan rule engine yang ketat. Output dapat bervariasi, biaya dapat lebih tinggi, dan hasilnya membutuhkan validasi tambahan.

### 10.3 Arsitektur yang Direkomendasikan untuk Proyek Portfolio Ini

Gunakan **pendekatan hybrid**:

```text
                 ┌───────────────────────┐
                 │ Interactive Frontend  │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │     Smart Living API  │
                 └───────────┬───────────┘
                             │
                  ┌──────────┴───────────┐
                  ▼                      ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ Deterministic    │   │ Optional AI      │
        │ Matching Engine  │   │ Enhancement Layer│
        └────────┬─────────┘   └────────┬─────────┘
                 │                      │
                 └──────────┬───────────┘
                            ▼
                  ┌──────────────────┐
                  │ Recipe Dataset   │
                  └──────────────────┘
```

**Pemeringkatan rekomendasi inti harus tetap deterministik.**

AI harus menjadi lapisan enhancement, bukan fondasi MVP.

Ini memungkinkan Anda menunjukkan prinsip penting dalam engineering/product:

> Gunakan logika deterministik ketika ketepatan dan konsistensi penting; gunakan AI ketika pemahaman bahasa, personalisasi, dan generasi benar-benar memberikan nilai tambah.

---

## 11. Roadmap AI

### Fase 1 — Tanpa ketergantungan AI

- Input bahan secara manual
- Normalisasi bahan
- Pencocokan resep deterministik
- Ranking
- Detail resep

### Fase 2 — Input dengan Bantuan AI

Gunakan LLM untuk mengubah bahasa natural yang tidak terstruktur menjadi object bahan yang telah dinormalisasi.

Contoh:

```text
Input:
"Saya punya 2 telur, setengah wortel, dan sisa ayam panggang"

Structured result:
{
  "ingredients": [
    {"name": "egg", "quantity": 2},
    {"name": "carrot", "quantity": 0.5},
    {"name": "chicken", "quantity": null}
  ]
}
```

Setelah itu, deterministic engine melakukan pencocokan resep yang sebenarnya.

### Fase 3 — Penjelasan & Substitusi dengan AI

AI dapat menjelaskan:

- Mengapa sebuah resep cocok.
- Menentukan bahan yang kurang mana yang paling penting.
- Kemungkinan substitusi bahan.
- Cara menyesuaikan resep dengan bahan yang tersedia.

### Fase 4 — Input Gambar

Izinkan pengguna mengunggah foto bahan makanan. Model yang memiliki kemampuan vision dapat mendeteksi kandidat bahan, lalu pengguna mengonfirmasi hasilnya sebelum pencocokan dilakukan.

Ini adalah enhancement masa depan, bukan ketergantungan MVP.

---

## 12. Strategi Data Resep

Untuk MVP, gunakan dataset resep yang telah dikurasi daripada menghasilkan semua resep secara dinamis.

Setiap resep sebaiknya memiliki struktur seperti:

```json
{
  "id": "recipe_001",
  "name": "Chicken Carrot Omelette",
  "ingredients": [
    {"name": "egg", "required": true},
    {"name": "chicken", "required": true},
    {"name": "carrot", "required": true},
    {"name": "onion", "required": false}
  ],
  "cookingTimeMinutes": 15,
  "difficulty": "easy",
  "steps": []
}
```

Untuk demo produk, dataset yang lebih kecil dan berkualitas tinggi lebih baik daripada dataset besar tetapi tidak konsisten.

Ukuran dataset MVP yang disarankan:

**50–100 recipes**.

Jumlah ini cukup untuk mendemonstrasikan recommendation engine sekaligus menjaga kualitas data tetap terkelola.

---

## 13. Kebutuhan Fungsional

### FR-01 Input Bahan

Sistem harus menerima daftar bahan yang dimasukkan secara manual.

### FR-02 Normalization

Sistem harus menormalisasi variasi sederhana pada nama bahan.

### FR-03 Recipe Matching

Sistem harus menghitung skor kecocokan untuk kandidat resep.

### FR-04 Ranking

Sistem harus mengurutkan resep dari relevansi tertinggi ke terendah.

### FR-05 Recommendations

Sistem harus mengembalikan hingga lima resep rekomendasi secara default.

### FR-06 Missing Ingredients

Sistem harus mengidentifikasi bahan resep yang tidak terdapat dalam daftar bahan pengguna.

### FR-07 Available Ingredients

Sistem harus mengidentifikasi bahan dari setiap resep yang sudah dimiliki pengguna.

### FR-08 Detail Resep

Sistem harus mengembalikan waktu memasak, tingkat kesulitan, bahan, dan langkah memasak.

### FR-09 Validation

API harus menolak request dengan format tidak valid dan memberikan respons error yang jelas.

### FR-10 Interactive Demo

Frontend harus menggunakan API dan menampilkan hasil rekomendasi nyata.

### FR-11 Documentation

Proyek harus menyertakan dokumentasi API serta contoh request/response.

---

## 14. Non-Kebutuhan Fungsional

### Performance

Target waktu respons API untuk request rekomendasi deterministik:

- p50 < 200 ms in local/development environment
- p95 < 500 ms untuk arsitektur target MVP

### Reliability

API harus mengembalikan hasil yang dapat diprediksi untuk dataset resep dan input bahan yang sama.

### Maintainability

Logika pencocokan harus dipisahkan dari kode HTTP/controller.

Lapisan konseptual yang disarankan:

```text
Route / Controller
        ↓
Service / Use Case
        ↓
Matching Engine
        ↓
Recipe Repository
```

### Keamanan

- Validasi payload request.
- Terapkan pembatasan laju request jika API dibuka untuk publik.
- Jangan pernah mengekspos secret provider/API ke frontend.
- Simpan API key AI hanya di sisi server.

### Observability / Pemantauan

Pantau metrik dasar seperti:

- jumlah request rekomendasi
- rata-rata waktu respons
- tingkat hasil kosong
- bahan yang paling sering dicari

Hindari menyimpan informasi identitas pribadi yang tidak diperlukan.

---

## 15. Prinsip Pengalaman Pengguna

1. **Cepat:** Pengguna harus dapat melihat rekomendasi resep dalam beberapa detik.
2. **Praktis:** Prioritaskan resep yang benar-benar dapat dibuat dari bahan yang tersedia.
3. **Transparan:** Tunjukkan alasan sebuah resep memperoleh skor kecocokan tertentu.
4. **Minim hambatan:** Input manual harus cepat dan toleran terhadap variasi penulisan.
5. **Kualitas portfolio:** Antarmuka harus terasa seperti produk nyata, bukan sekadar demo developer.

---

## 16. Kondisi Kosong & Edge Case

### Tidak ada bahan yang dimasukkan

Message:

> Tambahkan setidaknya satu bahan untuk mencari resep.

### Tidak ada resep yang cocok

Message:

> Kami tidak menemukan kecocokan yang kuat. Coba tambahkan bahan lain atau perluas daftar bahan Anda.

### Kecocokan dengan confidence rendah

Tampilkan rekomendasi dengan skor kecocokan yang lebih rendah secara jelas daripada menyembunyikan hasil yang masih berguna.

### Input tidak valid

Kembalikan error API terstruktur seperti:

```json
{
  "error": {
    "code": "INVALID_INGREDIENTS",
    "message": "Bahan harus berisi setidaknya satu item."
  }
}
```

---

## 17. Metrik Keberhasilan

Karena ini terutama merupakan proyek portfolio, keberhasilan harus diukur baik sebagai **produk** maupun sebagai **demonstrasi teknis**.

### Metrik Produk

- Tingkat keberhasilan rekomendasi
- Persentase pencarian yang menghasilkan setidaknya 3 resep relevan
- Tingkat hasil kosong
- Click-through rate dari kartu rekomendasi ke detail resep
- Jumlah pencarian ulang per sesi

### Metrik Teknis

- Latensi respons API
- Cakupan automated test untuk logika pencocokan
- Tingkat error
- Ketersediaan API
- Kualitas dokumentasi API

### Metrik Portfolio

Proyek yang kuat harus memudahkan reviewer memahami:

- Masalah pengguna yang diidentifikasi.
- Mengapa cakupan MVP tersebut dipilih.
- Bagaimana algoritma rekomendasi bekerja.
- Mengapa pencocokan deterministik menjadi sistem inti.
- Di mana AI memberikan nilai tambah.
- Bagaimana frontend dan backend berkomunikasi.
- Trade-off apa yang diambil.

---

## 18. Kriteria Penerimaan MVP

MVP dianggap selesai ketika:

- Pengguna dapat memasukkan bahan secara manual.
- Request mencapai endpoint API yang berfungsi.
- Bahan dinormalisasi secara konsisten untuk kebutuhan MVP.
- Engine mengurutkan resep secara deterministik.
- API mengembalikan hingga lima rekomendasi.
- Setiap rekomendasi berisi persentase kecocokan, bahan yang tersedia, bahan yang kurang, waktu memasak, tingkat kesulitan, dan langkah memasak.
- Frontend interaktif menampilkan respons API yang sebenarnya.
- Error API ditangani dengan baik.
- Automated test mencakup skenario pencocokan utama.
- Dokumentasi API mencakup contoh request/response.
- Proyek dapat dijalankan secara lokal melalui prosedur setup yang terdokumentasi.

---

## 19. Rekomendasi Tech Stack

PRD ini tidak mewajibkan stack teknologi tertentu, tetapi struktur berikut sesuai dengan tujuan portfolio.

### Frontend

- Next.js or React
- TypeScript
- Tailwind CSS

### Backend

- Node.js + TypeScript
- Fastify atau Express

Alternative:

- Python + FastAPI

### Database

Untuk iterasi pertama, dapat menggunakan salah satu:

- PostgreSQL, atau
- dataset JSON/seed yang version-controlled jika kecepatan pengembangan menjadi prioritas.

### Testing

- Unit test untuk matching engine
- Integration test untuk API
- Component test frontend bila diperlukan

### Documentation

- OpenAPI / Swagger
- README dengan arsitektur dan contoh

### AI

Optional OpenAI API integration in a nantinya phase.

---

## 20. Rekomendasi Arsitektur

```text
smart-living/
├── apps/
│   ├── web/                 # Interactive frontend
│   └── api/                 # REST API
│
├── packages/
│   ├── matching-engine/     # Deterministic recommendation logic
│   ├── shared-types/        # Shared TypeScript types/schemas
│   └── ui/                  # Optional shared UI components
│
├── data/
│   └── recipes/             # Recipe dataset / seed files
│
├── docs/
│   ├── architecture.md
│   └── api-examples.md
│
└── README.md
```

Struktur repository dapat berubah sesuai framework yang dipilih, tetapi matching engine sangat disarankan tetap terisolasi.

---

## 21. Product Backlog — MVP

### Epic 1 — Input Bahan

- Buat input bahan UI
- Dukung comma-separated values
- Validasi empty input
- Normalisasi huruf besar-kecil dan spasi
- Normalisasi common singular/plural forms

### Epic 2 — Recipe Dataset

- Definisikan skema resep
- Buat dataset resep awal
- Tambahkan 50–100 resep yang telah dikurasi
- Normalisasi nama bahan pada resep

### Epic 3 — Recommendation Engine

- Implementasikanasikan pencocokan bahan
- Implementasikanasikan perhitungan persentase kecocokan
- Implementasikanasikan deteksi bahan yang kurang
- Implementasikanasikan deteksi bahan yang tersedia
- Implementasikanasikan ranking
- Tambahkan unit test

### Epic 4 — API

- Implementasikanasikan endpoint rekomendasi
- Tambahkan validasi
- Tambahkan penanganan error
- Tambahkan endpoint health
- Tambahkan dokumentasi OpenAPI

### Epic 5 — Frontend Interaktif

- Buat landing page
- Buat input bahan
- Buat kartu rekomendasi
- Buat detail resep
- Tambahkan status pemuatan
- Tambahkan status kosong/error
- Tambahkan bagian showcase API

### Epic 6 — Portfolio Polish

- Tambahkan diagram arsitektur
- Tambahkan product studi kasus
- Tambahkan keputusan teknis
- Tambahkan screenshot/GIF demo
- Tambahkan instruksi deployment

---

## 22. Roadmap Masa Depan

### V1.1 — Input yang Lebih Baik

- Autocomplete bahan
- Dukungan kuantitas
- Kategori bahan
- Normalisasi sinonim yang lebih baik

### V1.2 — Personalisasi

- Preferensi pola makan
- Alergen
- Preferensi masakan
- Preferensi waktu memasak
- Tingkat kesulitan preference

### V1.3 — Peningkatan dengan AI

- Parsing bahan dari bahasa natural
- Penjelasan resep
- Saran substitusi bahan
- Adaptasi resep yang dipersonalisasi

### V1.4 — Input Gambar

- Upload foto kulkas/bahan makanan
- Computer vision / deteksi bahan multimodal
- Konfirmasi pengguna sebelum pencocokan

### V2 — Pantry Pintar

- Inventaris pantry
- Tanggal kedaluwarsa
- Rekomendasi **"gunakan ini terlebih dahulu"**
- Daftar belanja untuk bahan yang kurang
- Rekomendasi yang mempertimbangkan anggaran

---

## 23. Keputusan Produk Utama

### Decision 1 — API-terlebih dahulu

API adalah antarmuka produk kelas utama. Frontend merupakan client demonstrasi dari API.

**Alasan:** Pendekatan ini lebih baik untuk menunjukkan kemampuan backend/API engineering dan memungkinkan client mobile atau pihak ketiga di masa depan.

### Decision 2 — Deterministic core

Recommendation engine harus bersifat deterministik pada MVP.

**Alasan:** Hal ini membuat pencocokan mudah dijelaskan, diuji, murah, dan dapat diprediksi.

### Decision 3 — AI as an enhancement

AI pada awalnya harus digunakan untuk masalah yang memang memiliki keunggulan jelas dari pemahaman atau generasi bahasa.

**Alasan:** Hindari menambahkan LLM hanya karena proyek ingin memiliki AI. Setiap fitur AI harus memiliki manfaat pengguna yang dapat diukur.

### Decision 4 — Manual input terlebih dahulu

Input bahan manual adalah interaksi utama MVP.

**Alasan:** Ini meminimalkan cakupan dan memungkinkan masalah rekomendasi inti divalidasi terlebih dahulu. Input gambar tetap menjadi pengembangan alami di masa depan.

---

## 24. Risiko & Mitigasi

### Risiko: Kualitas data resep buruk

**Mitigasi:** Mulai dengan dataset yang lebih kecil dan telah dikurasi.

### Risiko: Ketidakkonsistenan penamaan bahan

**Mitigasi:** Perkenalkan kamus bahan kanonik dan lapisan normalisasi.

### Risiko: Rekomendasi terasa terlalu sederhana

**Mitigasi:** Perbaiki scoring dan ranking sebelum memperkenalkan generasi AI yang belum diperlukan.

### Risiko: AI meningkatkan kompleksitas tanpa nilai yang jelas

**Mitigasi:** Jadikan AI opsional dan terisolasi di balik batas service.

### Risiko: Proyek menjadi terlalu besar untuk MVP portfolio

**Mitigasi:** Prioritaskan satu journey yang sangat baik: input bahan → resep terurut → detail resep.

---

## 25. Narasi Portfolio

Proyek ini sebaiknya dipresentasikan sebagai product studi kasus, bukan hanya proyek coding.

Recommended narrative:

### Masalah

Orang memiliki bahan makanan sisa tetapi kesulitan menentukan apa yang harus dimasak.

### Insight

Peluang produk bukan sekadar pencarian resep, melainkan **decision support dari bahan ke pilihan masakan**.

### Strategi MVP

Mulai dengan pencocokan bahan-ke-resep deterministik untuk memvalidasi pengalaman inti dengan kompleksitas minimal.

### Strategi Engineering

Expose kemampuan pencocokan sebagai API yang dapat digunakan kembali dan bangun frontend interaktif sebagai salah satu consumer dari API tersebut.

### Strategi AI

Tambahkan AI hanya ketika AI benar-benar meningkatkan pemahaman bahasa natural, substitusi bahan, penjelasan, personalisasi, atau input berbasis gambar.

### Hasil

Produk yang ringkas tetapi kredibel, yang menunjukkan product discovery, prioritisasi, desain API, arsitektur backend, implementasi frontend, testing, dokumentasi, dan adopsi AI yang bertanggung jawab.

---

## 26. Pertanyaan Terbuka untuk Iterasi Berikutnya

Pertanyaan ini sebaiknya dijawab setelah baseline MVP selesai atau sebelum cakupan diperluas:

1. Apakah bahan pokok seperti garam, minyak, air, dan lada dianggap otomatis tersedia?
2. Apakah bahan yang kurang memengaruhi persentase kecocokan secara sama, atau bahan penting harus memiliki bobot lebih besar?
3. Apakah resep dengan lebih sedikit bahan yang kurang harus berada di atas resep dengan persentase mentah lebih tinggi tetapi banyak bahan yang masih harus dibeli?
4. Apakah kuantitas bahan perlu diperhitungkan pada versi berikutnya?
5. Strategi sumber/lisensi resep apa yang akan digunakan jika dataset berkembang signifikan?
6. Apakah API akan dipublikasikan dengan pembatasan laju request, atau terutama melayani portfolio demo?

---

## 27. North Star MVP

> **Dengan satu input sederhana, pengguna harus dapat memahami apa yang bisa mereka masak dari bahan yang sudah tersedia.**

MVP dianggap berhasil ketika pengguna dapat berpindah dari:

**"Saya punya bahan sisa ini"**

→ **"Berikut lima masakan praktis yang bisa saya buat."**

tanpa harus mencari secara manual di berbagai website resep.
