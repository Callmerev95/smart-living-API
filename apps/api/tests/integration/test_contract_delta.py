"""Integration test khusus Contract Delta v1.1.

Dipisah dari test reguler agar ketiga delta tidak diam-diam hilang saat refactor.
Sumber kontrak: `docs/content-schema.md` §A.9.
"""

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def post(ingredients: list[str], limit: int | None = None) -> dict:
    payload: dict = {"ingredients": ingredients}
    if limit is not None:
        payload["limit"] = limit
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    return response.json()


def by_id(data: dict, recipe_id: str) -> dict:
    return next(item for item in data["results"] if item["id"] == recipe_id)


# --------------------------------------------------------------------------- #
# Delta 1 — staple dikecualikan dari scoring
# --------------------------------------------------------------------------- #


class TestDelta1StapleExclusion:
    def test_staple_does_not_appear_in_missing(self) -> None:
        """User tanpa garam/minyak tidak boleh dianggap kekurangan bahan itu."""
        data = post(["telur", "ayam", "wortel"])
        for item in data["results"]:
            assert "salt" not in item["missingIngredients"]
            assert "cooking_oil" not in item["missingIngredients"]
            assert "water" not in item["missingIngredients"]

    def test_staple_does_not_appear_in_available(self) -> None:
        data = post(["telur", "ayam", "wortel", "garam", "minyak"])
        for item in data["results"]:
            assert "salt" not in item["availableIngredients"]
            assert "cooking_oil" not in item["availableIngredients"]

    def test_staple_still_listed_in_full_ingredients(self) -> None:
        """Field `ingredients` tetap memuat staple — user perlu tahu resep butuh minyak."""
        data = post(["telur", "ayam", "wortel"])
        omelet = by_id(data, "recipe_001")
        assert "cooking_oil" in omelet["ingredients"]
        assert "salt" in omelet["ingredients"]

    def test_score_is_100_when_only_staples_missing(self) -> None:
        """Semua bahan utama ada, tinggal garam & minyak -> 100%, bukan 67%."""
        data = post(["telur", "ayam", "wortel"])
        assert by_id(data, "recipe_001")["matchPercentage"] == 100

    def test_staple_excluded_from_denominator(self) -> None:
        """recipe_001 punya 3 required non-staple; 2 cocok -> 67%, bukan 2/6."""
        data = post(["telur", "ayam"])
        omelet = by_id(data, "recipe_001")
        assert omelet["matchPercentage"] == 67
        assert omelet["missingIngredients"] == ["carrot"]


# --------------------------------------------------------------------------- #
# Delta 2 — unknownIngredients di response, HTTP 200
# --------------------------------------------------------------------------- #


class TestDelta2UnknownIngredients:
    def test_unknown_reported_alongside_valid_results(self) -> None:
        data = post(["telur", "kangkung"])
        assert data["unknownIngredients"] == ["kangkung"]
        assert len(data["results"]) >= 1

    def test_all_unknown_returns_empty_results_not_error(self) -> None:
        data = post(["kangkung", "durian"])
        assert data["results"] == []
        assert data["unknownIngredients"] == ["kangkung", "durian"]

    def test_unknown_field_is_empty_array_when_all_recognized(self) -> None:
        data = post(["telur", "ayam"])
        assert data["unknownIngredients"] == []

    def test_unknown_is_deduplicated(self) -> None:
        data = post(["kangkung", "kangkung"])
        assert data["unknownIngredients"] == ["kangkung"]

    def test_unknown_keeps_input_form_not_canonical(self) -> None:
        """Tidak ada canonical untuk bahan tak dikenal — token asli yang dilaporkan."""
        data = post(["KANGKUNG"])
        assert data["unknownIngredients"] == ["kangkung"]

    def test_unknown_does_not_affect_scoring(self) -> None:
        """Bahan tak dikenal tidak menurunkan skor resep yang cocok."""
        with_unknown = post(["telur", "ayam", "wortel", "kangkung"])
        without = post(["telur", "ayam", "wortel"])
        assert with_unknown["results"] == without["results"]


# --------------------------------------------------------------------------- #
# Delta 3 — normalisasi transparan
# --------------------------------------------------------------------------- #


class TestDelta3TransparentNormalization:
    def test_raw_and_canonical_both_present(self) -> None:
        data = post(["telur", "ayam"])
        assert data["query"]["raw"] == ["telur", "ayam"]
        assert data["query"]["ingredients"] == ["egg", "chicken"]

    def test_canonical_excludes_unknown(self) -> None:
        data = post(["telur", "kangkung"])
        assert data["query"]["ingredients"] == ["egg"]
        assert "kangkung" not in data["query"]["ingredients"]

    def test_dedupe_across_aliases(self) -> None:
        """`telur`, `telur`, `eggs` semuanya canonical `egg`."""
        data = post(["telur", "telur", "eggs"])
        assert data["query"]["ingredients"] == ["egg"]

    def test_quantity_is_stripped_in_canonical(self) -> None:
        data = post(["2 butir telur", "100 gr ayam"])
        assert data["query"]["ingredients"] == ["egg", "chicken"]

    def test_raw_keeps_quantity_for_display(self) -> None:
        """`raw` menyimpan token setelah trim/lowercase, untuk ditampilkan ke user."""
        data = post(["2 butir telur"])
        assert data["query"]["raw"] == ["2 butir telur"]

    def test_case_insensitive(self) -> None:
        data = post(["TELUR", "Ayam"])
        assert data["query"]["ingredients"] == ["egg", "chicken"]

    def test_meta_reports_threshold(self) -> None:
        """Threshold dikembalikan agar client paham kenapa hasil sedikit."""
        data = post(["telur"])
        assert data["meta"]["threshold"] == 30
