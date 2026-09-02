---
title: Smart Living API
emoji: 🍳
colorFrom: yellow
colorTo: gray
sdk: docker
app_port: 8000
pinned: false
short_description: API rekomendasi resep dari bahan yang tersedia di kulkas
---

# Smart Living API

API yang mengubah bahan makanan sisa menjadi rekomendasi masakan. Masukkan bahan yang
ada, dapatkan resep terurut berdasarkan seberapa lengkap bahannya.

Recommendation engine bersifat **deterministik** — input dan dataset yang sama selalu
menghasilkan urutan yang sama.

- **Dokumentasi interaktif:** [`/docs`](/docs)
- **Kode sumber:** [github.com/Callmerev95/smart-living-API](https://github.com/Callmerev95/smart-living-API)
- **Dataset:** 60 resep masakan Indonesia, 94 bahan kanonik

## Contoh

```bash
curl -X POST https://callmerev95-smart-living-api.hf.space/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["telur", "ayam", "wortel"], "limit": 3}'
```

```json
{
  "query": {
    "raw": ["telur", "ayam", "wortel"],
    "ingredients": ["egg", "chicken", "carrot"]
  },
  "unknownIngredients": [],
  "results": [
    {
      "id": "recipe_001",
      "name": "Omelet Ayam Wortel",
      "matchPercentage": 100,
      "availableIngredients": ["egg", "chicken", "carrot"],
      "missingIngredients": [],
      "cookingTimeMinutes": 15,
      "difficulty": "easy"
    }
  ],
  "meta": { "count": 3, "limit": 3, "threshold": 30 }
}
```

## Cara kerja

```
input bebas          →  normalisasi        →  scoring         →  ranking
"2 butir telur"          egg                  0–100%             + tie-breaker
```

Tiga hal yang membedakan API ini:

- **Bahan pokok dikecualikan dari scoring.** Garam, minyak, air, lada, dan gula dianggap
  selalu tersedia, sehingga persentase mencerminkan bahan yang benar-benar menentukan.
- **Bahan tak dikenal dilaporkan, bukan ditolak.** Satu bahan di luar kamus tidak
  menggagalkan seluruh pencarian — ia dikembalikan lewat `unknownIngredients` dengan
  HTTP 200.
- **Normalisasi transparan.** Response membawa input asli dan hasil normalisasi, supaya
  client bisa menampilkan pemetaan `telur → egg`.

## Endpoint

| Endpoint | Keterangan |
|---|---|
| `POST /api/v1/recommendations` | Cari resep dari daftar bahan |
| `GET /api/v1/recipes/{id}` | Detail resep |
| `GET /api/v1/ingredients` | Kamus bahan kanonik + alias |
| `GET /api/v1/health` | Status dan jumlah data yang termuat |

## Tech stack

Python 3.12 · FastAPI · Pydantic v2 · Docker

Image ini dibangun dari `docker/api.Dockerfile` yang sama dengan yang diverifikasi CI
di repository GitHub. Deployment ke Space ini disinkronkan otomatis setiap kali CI
di branch `main` berhasil.

## Catatan

Space gratis akan tidur setelah beberapa waktu tidak diakses. Request pertama setelah
Space bangun bisa memerlukan beberapa detik.
