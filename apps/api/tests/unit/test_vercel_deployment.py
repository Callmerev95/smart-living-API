"""Test yang menjaga konfigurasi deployment Vercel tetap konsisten.

Entrypoint dan daftar dependency untuk Vercel berada di root repo, terpisah dari
`apps/api/pyproject.toml`. Tanpa test ini, keduanya mudah menyimpang tanpa
terdeteksi sampai deployment gagal di production.
"""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
REQUIREMENTS = REPO_ROOT / "requirements.txt"
PYPROJECT = REPO_ROOT / "apps" / "api" / "pyproject.toml"
ENTRYPOINT = REPO_ROOT / "index.py"
VERCEL_CONFIG = REPO_ROOT / "vercel.json"


def _parse_requirements(text: str) -> dict[str, str]:
    pinned: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "==" not in line:
            continue
        name, version = line.split("==", 1)
        pinned[name.strip().lower()] = version.strip()
    return pinned


def _runtime_dependencies() -> dict[str, str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    pinned: dict[str, str] = {}
    for spec in data["project"]["dependencies"]:
        name, version = spec.split("==", 1)
        # Buang extras: `uvicorn[standard]` -> `uvicorn`.
        pinned[name.split("[", 1)[0].strip().lower()] = version.strip()
    return pinned


class TestEntrypoint:
    def test_entrypoint_exists_at_repo_root(self) -> None:
        """Vercel mencari `index.py` di root project."""
        assert ENTRYPOINT.is_file()

    def test_entrypoint_exports_app(self) -> None:
        """Runtime memuat variabel top-level bernama `app`."""
        source = ENTRYPOINT.read_text(encoding="utf-8")
        assert "from apps.api.app.main import app" in source

    def test_entrypoint_has_no_logic(self) -> None:
        """Entrypoint hanya re-export; komposisi tetap di `app/main.py`."""
        source = ENTRYPOINT.read_text(encoding="utf-8")
        for forbidden in ("FastAPI(", "add_middleware", "include_router", "uvicorn"):
            assert forbidden not in source


class TestRequirements:
    def test_requirements_exists(self) -> None:
        assert REQUIREMENTS.is_file()

    def test_versions_match_pyproject(self) -> None:
        """Versi di requirements.txt harus sama dengan pyproject.toml."""
        requirements = _parse_requirements(REQUIREMENTS.read_text(encoding="utf-8"))
        runtime = _runtime_dependencies()

        mismatched = {
            name: (version, runtime[name])
            for name, version in requirements.items()
            if name in runtime and runtime[name] != version
        }
        assert not mismatched, f"versi menyimpang dari pyproject.toml: {mismatched}"

    def test_all_runtime_dependencies_present(self) -> None:
        """Setiap dependency runtime harus ada, kecuali uvicorn."""
        requirements = _parse_requirements(REQUIREMENTS.read_text(encoding="utf-8"))
        runtime = _runtime_dependencies()

        # Vercel memuat ASGI app langsung; server-nya disediakan platform.
        expected = set(runtime) - {"uvicorn"}
        assert expected <= set(requirements), f"kurang: {expected - set(requirements)}"

    def test_uvicorn_excluded(self) -> None:
        """Menyertakan uvicorn hanya memperbesar bundle tanpa dipakai."""
        requirements = _parse_requirements(REQUIREMENTS.read_text(encoding="utf-8"))
        assert "uvicorn" not in requirements

    def test_no_dev_dependencies(self) -> None:
        """pytest/ruff tidak boleh masuk bundle produksi."""
        requirements = _parse_requirements(REQUIREMENTS.read_text(encoding="utf-8"))
        for dev in ("pytest", "ruff", "httpx", "httpx2", "pytest-cov"):
            assert dev not in requirements


class TestVercelConfig:
    def test_config_is_valid_json(self) -> None:
        import json

        config = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))
        assert "functions" in config

    def test_excludes_heavy_directories(self) -> None:
        """Bundle harus ramping: web, test, dan artefak tidak ikut."""
        import json

        config = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))
        excluded = config["functions"]["index.py"]["excludeFiles"]

        for pattern in ("apps/web/**", "apps/api/tests/**", "docs/**", "**/__pycache__/**"):
            assert pattern in excluded

    def test_dataset_not_excluded(self) -> None:
        """`data/recipes/` WAJIB ikut ter-deploy — tanpa itu API gagal saat startup."""
        import json

        config = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))
        excluded = config["functions"]["index.py"]["excludeFiles"]
        assert "data/" not in excluded


class TestDatasetAvailability:
    def test_dataset_at_expected_location(self) -> None:
        """Layout Vercel sama dengan checkout: dataset di `<root>/data/recipes/`."""
        assert (REPO_ROOT / "data" / "recipes" / "recipes.json").is_file()
        assert (REPO_ROOT / "data" / "recipes" / "ingredients.json").is_file()

    def test_settings_finds_dataset_from_repo_root(self) -> None:
        """`_find_repo_root` harus menemukan dataset pada layout ini."""
        from app.core.config import REPO_ROOT as SETTINGS_ROOT

        assert (SETTINGS_ROOT / "data" / "recipes" / "recipes.json").is_file()
