"""Entrypoint untuk Vercel Python Runtime.

Vercel mencari `index.py` di root project dan memuat variabel top-level `app`
sebagai ASGI application (`docs/deployment.md` §1). File ini hanya mengatur
`sys.path` lalu re-export — seluruh komposisi aplikasi tetap di
`apps/api/app/main.py`.

Kenapa `sys.path` perlu diatur: seluruh modul di `apps/api/app/` memakai import
absolut `from app.xxx import ...` (61 tempat). Konvensi itu bekerja karena
`apps/api` selalu berada di `sys.path` — pytest mengaturnya lewat
`pythonpath = ["."]`, dan image Docker memakai `WORKDIR /app` dengan `app/`
sebagai subfolder. Vercel hanya menaruh root repo di `sys.path`, jadi baris di
bawah menyamakan kondisinya.

Dataset dibaca dari `data/recipes/` yang ikut ter-deploy; `Settings` menemukannya
lewat `_find_repo_root()` yang menelusuri ancestor sampai menemukan folder itu.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "apps" / "api"))

from app.main import app  # noqa: E402  (harus setelah sys.path diatur)

__all__ = ["app"]
