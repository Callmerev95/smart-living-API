"""Smoke test: membuktikan pipeline pytest berjalan sebelum ada fitur."""


def test_pytest_runs() -> None:
    assert True


def test_python_version_supported() -> None:
    import sys

    assert sys.version_info >= (3, 12)
