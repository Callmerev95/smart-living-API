"""Entrypoint untuk Vercel Python Runtime.

Vercel mencari `index.py` di root project dan memuat variabel top-level `app`
sebagai ASGI application (`docs/deployment.md` §1). File ini hanya re-export —
seluruh komposisi aplikasi tetap di `apps/api/app/main.py`.

`apps` dan `apps.api` adalah namespace package (tanpa `__init__.py`), sehingga
import di bawah bekerja karena root project berada di `sys.path` saat Vercel
memuat entrypoint.

Dataset dibaca dari `data/recipes/` yang ikut ter-deploy; `Settings` menemukannya
lewat `_find_repo_root()` yang menelusuri ancestor sampai menemukan folder itu.
"""

from apps.api.app.main import app

__all__ = ["app"]
