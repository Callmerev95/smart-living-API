"""Test untuk `IngredientNormalizer` (pipeline lengkap).

Berisi seluruh 14 test case wajib `docs/content-schema.md` §A.4.5.
"""

import pytest

from app.services.ingredient_normalizer import IngredientNormalizer, NormalizationResult

# Alias map minimal yang mencerminkan struktur `ingredients.json`.
# Canonical name juga hadir sebagai key — sesuai kontrak `get_alias_map()`.
ALIAS_MAP = {
    "egg": "egg",
    "telur": "egg",
    "telor": "egg",
    "eggs": "egg",
    "butir telur": "egg",
    "chicken": "chicken",
    "ayam": "chicken",
    "chicken breast": "chicken",
    "dada ayam": "chicken",
    "carrot": "carrot",
    "wortel": "carrot",
    "carrots": "carrot",
    "tomato": "tomato",
    "tomat": "tomato",
    "garlic": "garlic",
    "bawang putih": "garlic",
    "soy_sauce": "soy_sauce",
    "kecap": "soy_sauce",
    "kecap manis": "soy_sauce",
    "milk": "milk",
    "susu": "milk",
    "rice": "rice",
    "nasi": "rice",
}


@pytest.fixture
def normalizer() -> IngredientNormalizer:
    return IngredientNormalizer(ALIAS_MAP)


# --------------------------------------------------------------------------- #
# 14 test case wajib — docs/content-schema.md §A.4.5
# --------------------------------------------------------------------------- #


class TestSpecCases:
    def test_case01_trim_and_indonesian_alias(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize(" telur ").canonical == ("egg",)

    def test_case02_lowercase(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("TELUR").canonical == ("egg",)

    def test_case03_plural_alias(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("eggs").canonical == ("egg",)

    def test_case04_typo_alias(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("telor").canonical == ("egg",)

    def test_case05_specific_form_alias(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("chicken breast").canonical == ("chicken",)

    def test_case06_plural_rule(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("carrots").canonical == ("carrot",)

    def test_case07_strip_number(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("2 eggs").canonical == ("egg",)

    def test_case08_strip_number_and_unit(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("100 gr ayam").canonical == ("chicken",)

    def test_case09_strip_fraction(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("1/2 wortel").canonical == ("carrot",)

    def test_case10_split_and_trim(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize("telur,  ayam , wortel")
        assert result.canonical == ("egg", "chicken", "carrot")

    def test_case11_dedupe(self, normalizer: IngredientNormalizer) -> None:
        """`telur`, `telur`, dan `eggs` semuanya memetakan ke `egg`."""
        assert normalizer.normalize("telur, telur, eggs").canonical == ("egg",)

    def test_case12_unknown_ingredient_no_error(self, normalizer: IngredientNormalizer) -> None:
        """Bahan di luar kamus masuk `unknown`, bukan memicu exception (Delta 2)."""
        result = normalizer.normalize("kangkung")
        assert result.canonical == ()
        assert result.unknown == ("kangkung",)

    def test_case13_empty_input(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize("")
        assert result.canonical == ()
        assert result.unknown == ()

    def test_case14_empty_token_in_middle(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("telur, , ayam").canonical == ("egg", "chicken")


# --------------------------------------------------------------------------- #
# Delta v1.1 — normalisasi transparan (Delta 3) & unknown (Delta 2)
# --------------------------------------------------------------------------- #


class TestContractDelta:
    def test_raw_preserves_original_tokens(self, normalizer: IngredientNormalizer) -> None:
        """Delta 3: frontend butuh input asli untuk menampilkan `telur -> Telur`."""
        result = normalizer.normalize("Telur, AYAM")
        assert result.raw == ("telur", "ayam")
        assert result.canonical == ("egg", "chicken")

    def test_mixed_known_and_unknown(self, normalizer: IngredientNormalizer) -> None:
        """Delta 2: satu bahan tak dikenal tidak menggagalkan sisanya."""
        result = normalizer.normalize("telur, kangkung, ayam")
        assert result.canonical == ("egg", "chicken")
        assert result.unknown == ("kangkung",)

    def test_all_unknown(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize("kangkung, durian")
        assert result.canonical == ()
        assert result.unknown == ("kangkung", "durian")

    def test_unknown_is_deduped(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize("kangkung, kangkung")
        assert result.unknown == ("kangkung",)

    def test_unknown_keeps_lowercased_form(self, normalizer: IngredientNormalizer) -> None:
        """Unknown dilaporkan dalam bentuk ternormalisasi ringan, bukan mentah."""
        assert normalizer.normalize(" KANGKUNG ").unknown == ("kangkung",)


# --------------------------------------------------------------------------- #
# Determinisme & urutan
# --------------------------------------------------------------------------- #


class TestOrdering:
    def test_canonical_preserves_first_occurrence_order(
        self, normalizer: IngredientNormalizer
    ) -> None:
        result = normalizer.normalize("wortel, telur, ayam")
        assert result.canonical == ("carrot", "egg", "chicken")

    def test_dedupe_keeps_first_position(self, normalizer: IngredientNormalizer) -> None:
        """`telur` muncul pertama, jadi `egg` tetap di posisi awal."""
        result = normalizer.normalize("telur, ayam, eggs")
        assert result.canonical == ("egg", "chicken")

    def test_same_input_produces_same_output(self, normalizer: IngredientNormalizer) -> None:
        first = normalizer.normalize("telur, ayam, wortel")
        second = normalizer.normalize("telur, ayam, wortel")
        assert first == second

    def test_returns_tuples(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize("telur")
        assert isinstance(result.raw, tuple)
        assert isinstance(result.canonical, tuple)
        assert isinstance(result.unknown, tuple)


# --------------------------------------------------------------------------- #
# Input berupa list (payload API) & isolasi dependency
# --------------------------------------------------------------------------- #


class TestInputForms:
    def test_accepts_list(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize(["telur", "ayam"])
        assert result.canonical == ("egg", "chicken")

    def test_list_element_with_comma(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize(["telur, ayam", "wortel"])
        assert result.canonical == ("egg", "chicken", "carrot")

    def test_list_with_quantity(self, normalizer: IngredientNormalizer) -> None:
        result = normalizer.normalize(["2 telur", "100 gr ayam", "wortel"])
        assert result.canonical == ("egg", "chicken", "carrot")
        assert result.unknown == ()


class TestIsolation:
    def test_does_not_read_files(self) -> None:
        """Alias map di-inject; normalizer tidak menyentuh filesystem."""
        empty = IngredientNormalizer({})
        result = empty.normalize("telur")
        assert result.canonical == ()
        assert result.unknown == ("telur",)

    def test_alias_map_is_copied(self) -> None:
        """Mutasi map asal setelah konstruksi tidak boleh memengaruhi normalizer."""
        source = {"telur": "egg"}
        normalizer = IngredientNormalizer(source)
        source["ayam"] = "chicken"
        assert normalizer.normalize("ayam").unknown == ("ayam",)

    def test_no_fuzzy_matching(self, normalizer: IngredientNormalizer) -> None:
        """`telurr` mirip `telur` tapi tidak boleh ditebak (docs §A.4.4)."""
        assert normalizer.normalize("telurr").unknown == ("telurr",)

    def test_result_is_frozen(self, normalizer: IngredientNormalizer) -> None:
        import dataclasses

        result = normalizer.normalize("telur")
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.canonical = ()  # type: ignore[misc]

    def test_result_type(self, normalizer: IngredientNormalizer) -> None:
        assert isinstance(normalizer.normalize("telur"), NormalizationResult)


# --------------------------------------------------------------------------- #
# Multi-word & lookup order
# --------------------------------------------------------------------------- #


class TestLookupOrder:
    def test_multiword_alias_resolves(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("bawang putih").canonical == ("garlic",)

    def test_multiword_alias_with_quantity(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("3 siung bawang putih").canonical == ("garlic",)

    def test_multiword_alias_with_extra_whitespace(self, normalizer: IngredientNormalizer) -> None:
        assert normalizer.normalize("bawang   putih").canonical == ("garlic",)

    def test_canonical_name_used_directly(self, normalizer: IngredientNormalizer) -> None:
        """Input yang sudah canonical (`soy_sauce`) tetap dikenali."""
        assert normalizer.normalize("soy_sauce").canonical == ("soy_sauce",)

    def test_exact_match_wins_over_plural_strip(self, normalizer: IngredientNormalizer) -> None:
        """`carrots` ada di alias map, jadi tidak perlu jatuh ke aturan plural."""
        assert normalizer.normalize("carrots").canonical == ("carrot",)

    def test_plural_strip_falls_through_to_alias(self, normalizer: IngredientNormalizer) -> None:
        """`tomatoes` tidak ada di map; strip plural menemukan `tomato` (aturan §A.4.3)."""
        assert normalizer.normalize("tomatoes").canonical == ("tomato",)

    def test_plural_strip_on_unmapped_word_is_unknown(
        self, normalizer: IngredientNormalizer
    ) -> None:
        """`bananas` bukan alias; strip plural jadi `banana` yang juga tak dikenal."""
        assert normalizer.normalize("bananas").unknown == ("bananas",)
