"""Test untuk strip kuantitas & plural (pipeline langkah 5-6).

Referensi: `docs/content-schema.md` §A.4.2 dan §A.4.3.
"""

from app.services.ingredient_normalizer import strip_plural, strip_quantity


class TestStripQuantity:
    def test_integer_prefix(self) -> None:
        assert strip_quantity("2 eggs") == "eggs"

    def test_integer_with_unit(self) -> None:
        assert strip_quantity("2 butir telur") == "telur"

    def test_fraction(self) -> None:
        assert strip_quantity("1/2 wortel") == "wortel"

    def test_gram_unit(self) -> None:
        assert strip_quantity("100 gr ayam") == "ayam"

    def test_tablespoon_unit(self) -> None:
        assert strip_quantity("3 sdm kecap") == "kecap"

    def test_unit_attached_to_number(self) -> None:
        """`250ml` tanpa spasi tetap terbaca."""
        assert strip_quantity("250ml susu") == "susu"

    def test_decimal_with_comma(self) -> None:
        assert strip_quantity("1,5 kg ayam") == "ayam"

    def test_decimal_with_dot(self) -> None:
        assert strip_quantity("1.5 kg ayam") == "ayam"

    def test_clove_unit(self) -> None:
        assert strip_quantity("3 siung bawang putih") == "bawang putih"

    def test_no_number_unchanged(self) -> None:
        assert strip_quantity("telur") == "telur"
        assert strip_quantity("bawang putih") == "bawang putih"

    def test_number_in_the_middle_is_kept(self) -> None:
        """Hanya prefix yang dibuang — bukan sembarang angka."""
        assert strip_quantity("cabai 2 warna") == "cabai 2 warna"

    def test_number_only_falls_back_to_original(self) -> None:
        """Token tanpa nama bahan tidak boleh menjadi string kosong."""
        assert strip_quantity("2 kg") == "2 kg"
        assert strip_quantity("100") == "100"

    def test_unit_lookalike_word_not_stripped(self) -> None:
        """`liter` adalah satuan, tapi `2 literan` bukan — jangan potong sebagian kata."""
        assert strip_quantity("2 literan") == "literan"


class TestStripPlural:
    def test_trailing_s(self) -> None:
        assert strip_plural("carrots") == "carrot"

    def test_trailing_es_after_o(self) -> None:
        assert strip_plural("tomatoes") == "tomato"

    def test_trailing_es_after_ch(self) -> None:
        assert strip_plural("peaches") == "peach"

    def test_indonesian_word_untouched(self) -> None:
        assert strip_plural("telur") == "telur"
        assert strip_plural("ayam") == "ayam"

    def test_word_ending_in_ss_untouched(self) -> None:
        assert strip_plural("grass") == "grass"

    def test_word_ending_in_us_untouched(self) -> None:
        assert strip_plural("asparagus") == "asparagus"

    def test_word_ending_in_is_untouched(self) -> None:
        assert strip_plural("kangkungis") == "kangkungis"

    def test_short_word_untouched(self) -> None:
        """Kata sangat pendek tidak dipotong agar tidak merusak makna."""
        assert strip_plural("gas") == "gas"

    def test_singular_word_ending_in_e(self) -> None:
        """`rice` tidak boleh jadi `ric`."""
        assert strip_plural("rice") == "rice"

    def test_eggs(self) -> None:
        assert strip_plural("eggs") == "egg"
