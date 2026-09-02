"""Test untuk `app.core.config`."""

from pathlib import Path

import pytest

from app.core.config import REPO_ROOT, Settings, _find_repo_root, get_settings


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Buang env var yang bisa mengacaukan verifikasi nilai default."""
    for key in (
        "API_PORT",
        "CORS_ORIGINS",
        "LOG_LEVEL",
        "DEFAULT_LIMIT",
        "MAX_LIMIT",
        "MIN_MATCH_THRESHOLD",
        "MAX_INGREDIENTS_PER_REQUEST",
        "MAX_INGREDIENT_NAME_LENGTH",
        "RECIPES_PATH",
        "INGREDIENTS_PATH",
    ):
        monkeypatch.delenv(key, raising=False)


def _settings(**overrides: object) -> Settings:
    """Bangun Settings tanpa membaca `.env`, agar test tidak bergantung mesin."""
    return Settings(_env_file=None, **overrides)  # type: ignore[arg-type]


class TestDefaults:
    def test_server_defaults(self, clean_env: None) -> None:
        settings = _settings()
        assert settings.api_port == 8000
        assert settings.log_level == "INFO"

    def test_recommendation_defaults_match_content_schema(self, clean_env: None) -> None:
        """Nilai default wajib sama dengan docs/content-schema.md §A.7."""
        settings = _settings()
        assert settings.default_limit == 5
        assert settings.max_limit == 10
        assert settings.min_match_threshold == 30
        assert settings.max_ingredients_per_request == 30
        assert settings.max_ingredient_name_length == 60

    def test_cors_default_is_localhost_not_wildcard(self, clean_env: None) -> None:
        settings = _settings()
        assert settings.cors_origins == ["http://localhost:3000"]
        assert "*" not in settings.cors_origins

    def test_dataset_paths_default_to_repo_root(self, clean_env: None) -> None:
        settings = _settings()
        assert settings.recipes_path == REPO_ROOT / "data" / "recipes" / "recipes.json"
        assert settings.ingredients_path == REPO_ROOT / "data" / "recipes" / "ingredients.json"


class TestEnvOverride:
    def test_int_override(self, clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEFAULT_LIMIT", "3")
        monkeypatch.setenv("MIN_MATCH_THRESHOLD", "50")
        settings = _settings()
        assert settings.default_limit == 3
        assert settings.min_match_threshold == 50

    def test_cors_comma_separated(self, clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test")
        assert _settings().cors_origins == ["http://a.test", "http://b.test"]

    def test_cors_json_array(self, clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CORS_ORIGINS", '["http://a.test","http://b.test"]')
        assert _settings().cors_origins == ["http://a.test", "http://b.test"]

    def test_cors_single_value(self, clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CORS_ORIGINS", "http://only.test")
        assert _settings().cors_origins == ["http://only.test"]


class TestPathResolution:
    def test_relative_path_resolved_against_repo_root(
        self, clean_env: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Path relatif tidak boleh bergantung pada cwd."""
        monkeypatch.setenv("RECIPES_PATH", "data/recipes/other.json")
        settings = _settings()
        assert settings.recipes_path.is_absolute()
        assert settings.recipes_path == (REPO_ROOT / "data" / "recipes" / "other.json").resolve()

    def test_absolute_path_kept_as_is(
        self, clean_env: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RECIPES_PATH", "/tmp/custom-recipes.json")
        assert _settings().recipes_path == Path("/tmp/custom-recipes.json")


class TestFindRepoRoot:
    """Pencarian root harus bekerja untuk layout checkout maupun image Docker.

    Sebelumnya root dihitung dengan `parents[4]` yang meledak (`IndexError`) di
    dalam container karena layout-nya lebih datar — dan itu terjadi saat import,
    sehingga server gagal start sebelum sempat membaca env var.
    """

    def test_checkout_layout(self, tmp_path: Path) -> None:
        root = tmp_path / "repo"
        config_file = root / "apps" / "api" / "app" / "core" / "config.py"
        config_file.parent.mkdir(parents=True)
        config_file.touch()
        (root / "data" / "recipes").mkdir(parents=True)

        assert _find_repo_root(config_file) == root.resolve()

    def test_docker_flat_layout(self, tmp_path: Path) -> None:
        """`/app/app/core/config.py` dengan dataset di `/app/data/recipes`."""
        root = tmp_path / "app"
        config_file = root / "app" / "core" / "config.py"
        config_file.parent.mkdir(parents=True)
        config_file.touch()
        (root / "data" / "recipes").mkdir(parents=True)

        assert _find_repo_root(config_file) == root.resolve()

    def test_shallow_path_does_not_raise(self, tmp_path: Path) -> None:
        """Path dengan sedikit ancestor tidak boleh menimbulkan IndexError."""
        config_file = tmp_path / "config.py"
        config_file.touch()

        assert _find_repo_root(config_file) == Path.cwd()

    def test_falls_back_to_cwd_without_dataset(self, tmp_path: Path) -> None:
        config_file = tmp_path / "a" / "b" / "config.py"
        config_file.parent.mkdir(parents=True)
        config_file.touch()

        assert _find_repo_root(config_file) == Path.cwd()

    def test_nearest_ancestor_wins(self, tmp_path: Path) -> None:
        """Bila ada dua kandidat, yang terdekat dari config.py yang dipakai."""
        outer = tmp_path / "outer"
        inner = outer / "inner"
        config_file = inner / "app" / "core" / "config.py"
        config_file.parent.mkdir(parents=True)
        config_file.touch()
        (outer / "data" / "recipes").mkdir(parents=True)
        (inner / "data" / "recipes").mkdir(parents=True)

        assert _find_repo_root(config_file) == inner.resolve()

    def test_module_level_root_points_at_real_dataset(self) -> None:
        """REPO_ROOT hasil pencarian harus benar-benar memuat dataset."""
        assert (REPO_ROOT / "data" / "recipes" / "recipes.json").is_file()


class TestSingleton:
    def test_get_settings_is_cached(self) -> None:
        get_settings.cache_clear()
        assert get_settings() is get_settings()
        get_settings.cache_clear()
