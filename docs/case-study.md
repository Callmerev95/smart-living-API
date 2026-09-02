# Studi Kasus Produk — Smart Living API

**Peran:** Product Manager + Backend/API Developer + Full-stack Developer
**Durasi:** MVP dari PRD sampai siap deploy
**Hasil:** API deterministik + frontend demo, 60 resep terkurasi, 704 test otomatis

---

## Masalah

Orang punya bahan sisa di kulkas, tapi tidak tahu harus memasak apa.

Kedengarannya sepele, tapi konsekuensinya nyata dan berulang setiap minggu:

- Bahan kedaluwarsa sebelum terpakai — uang terbuang, sampah bertambah.
- Beli makanan di luar padahal bahan di rumah masih ada.
- Menghabiskan waktu membuka lima situs resep, menemukan resep yang butuh delapan bahan
  yang tidak dimiliki.

Yang menarik: masalahnya **bukan** kekurangan resep. Internet dipenuhi resep. Masalahnya
arah pencariannya terbalik. Situs resep meminta kita memilih masakan lalu memberi daftar
belanja. Yang dibutuhkan justru sebaliknya — mulai dari apa yang sudah ada.

---

## Insight

> Peluangnya bukan pencarian resep, melainkan **decision support dari bahan ke pilihan
> masakan.**

Perbedaannya menentukan seluruh desain produk.

Kalau ini masalah pencarian, yang dibutuhkan adalah indeks besar dan relevansi teks —
semakin banyak resep semakin baik. Kalau ini masalah pengambilan keputusan, yang
dibutuhkan adalah **sedikit pilihan yang benar-benar bisa dieksekusi**, dengan alasan yang
jelas mengapa pilihan itu muncul.

Konsekuensi konkretnya: 60 resep terkurasi lebih berguna daripada 5.000 resep hasil
scraping. Dan menampilkan *"kamu tinggal beli bawang"* lebih berharga daripada
menampilkan skor relevansi tanpa penjelasan.

---

## Keputusan scope

Empat keputusan besar, semuanya tentang apa yang **tidak** dikerjakan.

### 1. Input manual dulu, bukan foto

Deteksi bahan dari foto kulkas adalah fitur yang paling menarik untuk didemokan. Ia juga
yang paling mudah menyembunyikan kegagalan produk.

Kalau rekomendasinya tidak berguna, deteksi foto yang akurat pun tidak menyelamatkan
apa pun — user tetap tidak tahu harus memasak apa. Jadi masalah inti harus divalidasi
lebih dulu: apakah pencocokan bahan-ke-resep benar-benar membantu?

Input manual membuat pertanyaan itu bisa dijawab dalam hitungan hari, bukan minggu.

### 2. Deterministik dulu, bukan LLM

Menaruh LLM di jantung recommendation engine akan membuat proyek terlihat modern. Tapi
untuk masalah ini, LLM justru lebih buruk pada dimensi yang paling penting:

| | Deterministik | LLM |
|---|---|---|
| Hasil untuk input sama | Selalu identik | Bisa berbeda |
| Bisa dijelaskan ke user | "3 dari 4 bahan ada" | Sulit |
| Biaya per request | Nol | Ada |
| Bisa diuji otomatis | Ya, presisi | Perlu toleransi |

User yang melihat *"80% cocok"* berhak tahu dari mana angka itu. Formula
`matched / required × 100` bisa dijelaskan dalam satu kalimat. Output LLM tidak.

AI tetap punya tempat — untuk memahami *"saya punya dua telur dan sisa ayam panggang"* —
tapi sebagai lapisan parsing di depan engine, bukan pengganti engine. Boundary-nya sudah
disiapkan; implementasinya belum dibutuhkan.

### 3. API-first, frontend sebagai client

Frontend dibangun sebagai konsumen API, bukan aplikasi yang kebetulan punya backend.
Business logic tidak pernah masuk ke React.

Ini bukan preferensi arsitektur murni — ia keputusan produk. API yang bisa dipakai
sendiri membuka jalan untuk client mobile, integrasi pihak ketiga, dan pengujian yang
tidak bergantung UI. Dan ia memaksa kontrak data dipikirkan lebih awal.

### 4. 60 resep, bukan 500

Dataset kecil yang terkurasi mengalahkan dataset besar yang tidak konsisten. Alasannya
teknis sekaligus produk: dengan 60 resep, setiap resep bisa diperiksa kelayakan
kulinernya, dan **overlap bahan** bisa dirancang dengan sengaja.

Overlap itu yang membuat rekomendasi terasa hidup. Kalau setiap resep memakai bahan yang
sama sekali berbeda, satu input hanya akan cocok ke satu resep — dan ranking kehilangan
makna. Dataset dirancang supaya input umum seperti `telur, ayam, wortel` menghasilkan
sebaran skor 100%, 50%, 40%, 33% — bukan semuanya 100% atau semuanya 0%.

---

## Keputusan produk yang muncul di tengah jalan

Tiga keputusan ini tidak ada di PRD awal. Semuanya muncul dari pertanyaan terbuka yang
sengaja dicatat lalu dijawab sebelum implementasi.

### Bahan pokok tidak dihitung

PRD mencatat pertanyaan terbuka: *"Apakah bahan pokok seperti garam, minyak, air, dan
lada dianggap otomatis tersedia?"*

Awalnya terasa seperti detail teknis. Ternyata ia menentukan apakah angka yang dilihat
user bermakna atau menyesatkan.

Ambil kasus nyata dari dataset. Resep Omelet Ayam Wortel butuh: telur, ayam, wortel,
bawang merah, garam, lada, minyak. User punya telur, ayam, wortel.

| Perlakuan | Hasil | Yang dirasakan user |
|---|---|---|
| Garam & minyak dihitung | 3/6 = **50%** | "Setengah bahan kurang, mungkin nanti saja" |
| Garam & minyak dikecualikan | 3/3 = **100%** | "Bisa langsung masak sekarang" |

Angka 50% secara teknis benar tapi secara produk salah — ia menghalangi user dari resep
yang sebenarnya bisa langsung dibuat. Dapur mana pun yang bisa memasak sudah punya garam
dan minyak.

Keputusan: bahan dengan flag `staple: true` dikecualikan dari denominator, tidak muncul
di daftar "perlu dibeli", tapi **tetap ditampilkan** di daftar bahan lengkap — user harus
tahu resepnya butuh minyak. Halaman detail resep juga memuat catatan eksplisit yang
menjelaskan aturan ini, supaya angkanya tidak terasa seperti sihir.

**Trade-off:** asumsinya salah untuk dapur yang benar-benar kosong. Untuk audiens produk
ini, asumsinya jauh lebih sering benar.

### Bahan tak dikenal dilaporkan, bukan ditolak

Kamus berisi 94 bahan. Pasti ada yang di luar itu.

Pilihan yang tersedia: tolak seluruh request, abaikan diam-diam, atau tebak dengan fuzzy
matching.

Menolak seluruh request paling merusak — user menulis lima bahan, satu di antaranya
`kangkung`, dan kehilangan rekomendasi untuk empat bahan lainnya. Mengabaikan diam-diam
lebih halus tapi membingungkan: kenapa hasilnya sedikit? Fuzzy matching terdengar pintar
sampai `kangkung` dipetakan menjadi `kacang` dan user diberi resep yang salah.

Keputusan: bahan tak dikenal dikembalikan dalam `unknownIngredients` dengan HTTP 200.
Pencarian tetap berjalan dengan bahan yang dikenali, dan frontend menampilkan chip
"tidak dikenali" supaya user paham. Tidak ada yang ditebak.

### Normalisasi ditampilkan, bukan disembunyikan

Sistem mengubah `telur` menjadi `egg` secara internal. Pertanyaannya: perlukah user
tahu?

Salah satu prinsip UX di PRD adalah transparansi — user harus paham mengapa sebuah resep
mendapat skor tertentu. Skor dihitung dari bahan hasil normalisasi. Kalau user tidak tahu
bahan apa yang sebenarnya dipakai sistem, skornya tidak bisa dipercaya.

Keputusan: response membawa input asli **dan** hasil normalisasi. Frontend menampilkannya
sebagai chip `telur → Telur`. Efek sampingnya menyenangkan: saat demo, orang langsung
melihat bahwa sistem "mengerti" input mereka — dan bug normalisasi jadi kelihatan tanpa
membuka log.

---

## Bagaimana keberhasilan diukur

Sebagai produk:

| Metrik | Target | Status |
|---|---|---|
| Pencarian menghasilkan ≥3 resep relevan | Mayoritas input umum | Terpenuhi — 5, 3, dan 5 hasil untuk tiga contoh input |
| Sebaran skor, bukan semua sama | Ada gradasi | Terpenuhi — 100/50/50/40/33% |
| Hasil kosong hanya bila memang tidak ada | Tanpa error | Terpenuhi — `results: []` dengan HTTP 200 |
| Alasan skor bisa dipahami user | Ditampilkan | Terpenuhi — available, missing, catatan bahan pokok |

Sebagai demonstrasi teknis:

| Metrik | Target | Hasil |
|---|---|---|
| Latency p50 | < 200 ms | 1,1 ms |
| Latency p95 | < 500 ms | 1,4 ms |
| Coverage logika inti | ≥ 90% | 100% |
| Determinisme | Input sama → hasil sama | Diuji dengan input dan urutan data teracak |
| Dataset valid | 100% aturan | 16 aturan validasi, dicek di CI |

Latency jauh di bawah target karena dataset dimuat sekali saat startup dan seluruh
pencocokan berjalan di memori. Ini konsekuensi langsung dari keputusan JSON + repository
singleton.

---

## Trade-off yang diambil

Setiap keputusan punya harga. Yang dibayar:

**Bahasa natural belum didukung.** *"Saya punya dua telur dan sisa ayam panggang"* tidak
bisa diproses. Harga dari memilih determinisme.

**Kuantitas diabaikan.** Sistem tahu user punya telur, tidak tahu berapa. Resep untuk
empat porsi direkomendasikan meski bahannya cukup untuk satu. Menambahkan kuantitas
berarti mengumpulkan data kuantitas untuk 60 resep dan menangani konversi satuan —
belum sepadan untuk MVP.

**Dataset kecil.** 60 resep berarti ada kombinasi bahan yang belum tercakup. Sengaja:
kualitas dan overlap yang dirancang lebih penting daripada jumlah.

**Tanpa personalisasi.** Preferensi diet, alergen, dan riwayat butuh akun user, dan akun
user butuh database. Rantai kebutuhan itu berhenti di luar batas MVP.

**Satu build web per environment.** `NEXT_PUBLIC_API_BASE_URL` dibakar saat build, jadi
image Docker web tidak bisa dipakai ulang untuk URL API berbeda. Konsekuensi cara Next.js
menangani variabel client.

---

## Yang akan dilakukan berbeda

**Menulis validator dataset lebih awal.** Validator dibuat sebelum dataset diisi — itu
keputusan yang tepat. Tapi aturan "setiap bahan yang disebut di langkah memasak harus
terdaftar di `ingredients`" baru diperiksa setelah 60 resep selesai, dan ternyata 14 resep
melanggarnya. Memasukkan aturan itu ke validator sejak awal akan mencegah 14 perbaikan
manual.

**Menguji Docker lebih awal.** Dockerfile dibuat di fase terakhir, dan langsung menemukan
dua bug yang tidak pernah muncul dalam 500 test: perhitungan path root yang mengasumsikan
struktur direktori checkout, dan file konfigurasi pnpm yang tidak ter-mount. Membangun
image di fase awal akan mengungkap asumsi lingkungan lebih cepat.

**Mengambil keputusan bahan pokok sebelum menulis engine.** Keputusan itu mengubah rumus
scoring, bentuk response, dan copy UI. Karena ia diputuskan setelah dokumen arsitektur
selesai, tiga dokumen harus diberi catatan delta. Pertanyaan yang menyentuh rumus inti
sebaiknya dijawab sebelum implementasi, bukan di tengah jalan.

---

## Yang membuat proyek ini bukan latihan coding

Tiga hal yang biasanya hilang dari proyek portfolio:

**Batas cakupan tercatat sebagai keputusan, bukan kekurangan.** Setiap yang tidak
dikerjakan punya alasan yang bisa dijelaskan — bukan "belum sempat".

**Pertanyaan terbuka dicatat sebelum dijawab.** PRD memuat enam pertanyaan yang sengaja
ditunda. Tiga di antaranya kemudian mengubah kontrak API, dan perubahannya
terdokumentasi sebagai delta — bukan diam-diam mengubah desain lama.

**Aturan arsitektur ditegakkan mesin, bukan niat.** Larangan "domain layer tidak boleh
mengimpor framework" diperiksa oleh test yang mem-parsing AST. Pelanggaran membuat CI
merah. Aturan yang hanya tertulis di dokumen akan dilanggar dalam tiga bulan.

---

## Dokumen terkait

| Dokumen | Isi |
|---|---|
| [`prd.md`](prd.md) | Product requirement lengkap, termasuk pertanyaan terbuka |
| [`technical-architecture.md`](technical-architecture.md) | Keputusan arsitektur dan alasannya |
| [`content-schema.md`](content-schema.md) | Kontrak data, aturan scoring, Contract Delta v1.1 |
| [`development-roadmap.md`](development-roadmap.md) | Fase pengembangan dan exit criteria |
| [`../README.md`](../README.md) | Cara menjalankan dan contoh API |
