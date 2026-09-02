"""Konfigurasi aplikasi.

Semua konstanta yang bisa diubah lewat environment berada di sini — bukan tersebar
sebagai angka literal di route/service. Nilai default mengikuti
`docs/content-schema.md` §A.7.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _find_repo_root(config_file: Path) -> Path:
    """Cari direktori yang memuat dataset, mulai dari lokasi file ini.

    Menghitung jumlah tingkat secara kaku (`parents[4]`) hanya benar untuk layout
    checkout dan meledak di dalam container Docker yang layout-nya lebih datar
    (`/app/app/core/config.py`). Pencarian berbasis penanda `data/recipes`
    bekerja untuk keduanya:

    - checkout: ``<root>/apps/api/app/core/config.py`` -> ``<root>``
    - image:    ``/app/app/core/config.py``            -> ``/app``
    """
    for candidate in config_file.resolve().parents:
        if (candidate / "data" / "recipes").is_dir():
            return candidate

    # Dataset tidak ditemukan di ancestor mana pun. Kembalikan cwd agar error yang
    # muncul nanti berasal dari repository (pesan jelas: file tidak ditemukan),
    # bukan IndexError saat import.
    return Path.cwd()


REPO_ROOT = _find_repo_root(Path(__file__))


class Settings(BaseSettings):
    """Setting aplikasi, dibaca dari environment variable atau `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Server ---
    api_port: int = 8000
    # NoDecode: matikan JSON-parsing otomatis agar validator di bawah bisa menerima
    # format comma-separated maupun JSON array.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    log_level: str = "INFO"

    # --- Recommendation (content-schema.md §A.7) ---
    default_limit: int = 5
    max_limit: int = 10
    min_match_threshold: int = 30
    max_ingredients_per_request: int = 30
    max_ingredient_name_length: int = 60

    # --- Dataset ---
    recipes_path: Path = REPO_ROOT / "data" / "recipes" / "recipes.json"
    ingredients_path: Path = REPO_ROOT / "data" / "recipes" / "ingredients.json"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Terima `"a,b"` maupun JSON array, supaya `.env` tetap enak ditulis."""
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @field_validator("recipes_path", "ingredients_path", mode="after")
    @classmethod
    def _resolve_dataset_path(cls, value: Path) -> Path:
        """Path relatif diselesaikan terhadap root repo, bukan cwd."""
        return value if value.is_absolute() else (REPO_ROOT / value).resolve()


@lru_cache
def get_settings() -> Settings:
    """Settings sebagai singleton — dibaca sekali per proses."""
    return Settings()
