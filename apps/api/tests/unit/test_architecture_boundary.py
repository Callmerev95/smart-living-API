"""Test yang menegakkan aturan dependency `AGENTS.md` §4 secara otomatis.

Pelanggaran boundary harus tertangkap CI, bukan bergantung pada review manual.
Implementasi memakai AST agar tidak salah tangkap kata di dalam komentar atau string.
"""

import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2] / "app"

# Modul yang dilarang di domain layer (`AGENTS.md` §4).
FORBIDDEN_IN_DOMAIN = frozenset(
    {
        "fastapi",
        "starlette",
        "pydantic",
        "pydantic_settings",
        "httpx",
        "requests",
        "urllib",
        "openai",
        "sqlalchemy",
        "psycopg",
        "asyncpg",
        "sqlite3",
    }
)

# Domain tidak boleh tahu layer di atasnya.
FORBIDDEN_APP_PREFIXES_IN_DOMAIN = ("app.api", "app.schemas", "app.services", "app.core")

# Repository hanya boleh menyentuh domain + stdlib.
FORBIDDEN_IN_REPOSITORIES = frozenset(
    {"fastapi", "starlette", "pydantic", "httpx", "requests", "openai"}
)


def _iter_python_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.rglob("*.py") if p.name != "__init__.py")


def _imported_modules(path: Path) -> set[str]:
    """Kumpulkan nama modul yang di-import, dari AST — bukan pencarian teks."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)

    return modules


def _root_package(module: str) -> str:
    return module.split(".", 1)[0]


def _called_names(path: Path) -> set[str]:
    """Nama fungsi/atribut yang dipanggil, untuk mendeteksi akses file langsung."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)

    return names


class TestDomainLayer:
    def test_domain_has_no_framework_import(self) -> None:
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "domain"):
            for module in _imported_modules(path):
                if _root_package(module) in FORBIDDEN_IN_DOMAIN:
                    violations.append(f"{path.relative_to(APP_ROOT)} mengimpor `{module}`")

        assert not violations, "domain layer harus bebas framework:\n" + "\n".join(violations)

    def test_domain_does_not_depend_on_upper_layers(self) -> None:
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "domain"):
            for module in _imported_modules(path):
                if module.startswith(FORBIDDEN_APP_PREFIXES_IN_DOMAIN):
                    violations.append(f"{path.relative_to(APP_ROOT)} mengimpor `{module}`")

        assert not violations, "domain tidak boleh tahu layer di atasnya:\n" + "\n".join(violations)

    def test_domain_does_not_read_files(self) -> None:
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "domain"):
            called = _called_names(path)
            for forbidden in ("open", "read_text", "read_bytes", "load", "loads"):
                if forbidden in called:
                    violations.append(f"{path.relative_to(APP_ROOT)} memanggil `{forbidden}`")

        assert not violations, "domain tidak boleh mengakses data:\n" + "\n".join(violations)

    def test_matching_engine_does_not_sort(self) -> None:
        """Ranking milik `ranking.py`; engine dan scoring tidak boleh mengurutkan."""
        violations: list[str] = []

        for filename in ("engine.py", "scoring.py"):
            path = APP_ROOT / "domain" / "matching" / filename
            called = _called_names(path)
            if "sorted" in called or "sort" in called:
                violations.append(f"{filename} melakukan sorting")

        assert not violations, "\n".join(violations)


class TestRepositoryLayer:
    def test_repositories_have_no_framework_import(self) -> None:
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "repositories"):
            for module in _imported_modules(path):
                if _root_package(module) in FORBIDDEN_IN_REPOSITORIES:
                    violations.append(f"{path.relative_to(APP_ROOT)} mengimpor `{module}`")

        assert not violations, "repository harus bebas framework:\n" + "\n".join(violations)

    def test_repositories_do_not_import_services(self) -> None:
        """Arah dependency: service -> repository, bukan sebaliknya."""
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "repositories"):
            for module in _imported_modules(path):
                if module.startswith(("app.services", "app.api", "app.schemas")):
                    violations.append(f"{path.relative_to(APP_ROOT)} mengimpor `{module}`")

        assert not violations, "\n".join(violations)


class TestApiLayer:
    def test_routes_do_not_access_data_directly(self) -> None:
        """Route hanya boleh lewat service (`docs/component-architecture.md` §25 Rule 2)."""
        api_dir = APP_ROOT / "api"
        if not api_dir.exists():
            return

        violations: list[str] = []

        for path in _iter_python_files(api_dir):
            called = _called_names(path)
            for forbidden in ("open", "read_text", "load", "loads"):
                if forbidden in called:
                    violations.append(f"{path.relative_to(APP_ROOT)} memanggil `{forbidden}`")

            for module in _imported_modules(path):
                if module.startswith("app.repositories"):
                    violations.append(
                        f"{path.relative_to(APP_ROOT)} mengimpor repository langsung: `{module}`"
                    )

        assert not violations, "route tidak boleh akses data langsung:\n" + "\n".join(violations)

    def test_routes_do_not_import_matching_domain(self) -> None:
        """Route tidak boleh menghitung skor — algoritma diakses lewat service."""
        api_dir = APP_ROOT / "api"
        if not api_dir.exists():
            return

        violations = [
            f"{path.relative_to(APP_ROOT)} mengimpor `{module}`"
            for path in _iter_python_files(api_dir)
            for module in _imported_modules(path)
            if module.startswith("app.domain.matching")
        ]

        assert not violations, "\n".join(violations)


class TestServiceLayer:
    def test_services_do_not_import_web_framework(self) -> None:
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "services"):
            for module in _imported_modules(path):
                if _root_package(module) in {"fastapi", "starlette", "httpx", "requests"}:
                    violations.append(f"{path.relative_to(APP_ROOT)} mengimpor `{module}`")

        assert not violations, "service harus bisa diuji tanpa server:\n" + "\n".join(violations)

    def test_services_do_not_read_files(self) -> None:
        """Akses data lewat repository, bukan file langsung."""
        violations: list[str] = []

        for path in _iter_python_files(APP_ROOT / "services"):
            called = _called_names(path)
            for forbidden in ("open", "read_text", "loads"):
                if forbidden in called:
                    violations.append(f"{path.relative_to(APP_ROOT)} memanggil `{forbidden}`")

        assert not violations, "\n".join(violations)


class TestCheckerItself:
    def test_detects_forbidden_import(self, tmp_path: Path) -> None:
        """Guard: pastikan checker benar-benar bisa gagal, bukan selalu lolos."""
        sample = tmp_path / "bad.py"
        sample.write_text("import fastapi\nfrom app.api.v1 import router\n", encoding="utf-8")
        modules = _imported_modules(sample)
        assert "fastapi" in modules
        assert any(m.startswith("app.api") for m in modules)

    def test_ignores_words_in_comments_and_strings(self, tmp_path: Path) -> None:
        """AST tidak boleh salah tangkap kata `fastapi` di komentar atau docstring."""
        sample = tmp_path / "clean.py"
        sample.write_text(
            '"""Modul ini tidak memakai fastapi."""\n'
            "# fastapi juga disebut di komentar\n"
            'x = "openai"\n',
            encoding="utf-8",
        )
        assert _imported_modules(sample) == set()

    def test_detects_call_names(self, tmp_path: Path) -> None:
        sample = tmp_path / "reader.py"
        sample.write_text("import json\njson.loads('{}')\nopen('x')\n", encoding="utf-8")
        called = _called_names(sample)
        assert "loads" in called
        assert "open" in called
