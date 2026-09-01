"""Test untuk `app.core.config`."""

from pathlib import Path

import pytest

from app.core.config import REPO_ROOT, Settings, get_settings


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


class TestSingleton:
    def test_get_settings_is_cached(self) -> None:
        get_settings.cache_clear()
        assert get_settings() is get_settings()
        get_settings.cache_clear()
