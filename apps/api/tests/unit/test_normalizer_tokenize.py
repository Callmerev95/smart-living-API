"""Test untuk tokenizer normalizer (pipeline langkah 1-4)."""

from app.services.ingredient_normalizer import tokenize


class TestTokenize:
    def test_split_on_comma_with_trim(self) -> None:
        assert tokenize("telur,  ayam , wortel") == ("telur", "ayam", "wortel")

    def test_lowercase(self) -> None:
        assert tokenize(" TELUR ") == ("telur",)

    def test_empty_string(self) -> None:
        assert tokenize("") == ()

    def test_only_whitespace(self) -> None:
        assert tokenize("   ") == ()

    def test_empty_token_in_the_middle_is_dropped(self) -> None:
        assert tokenize("telur, , ayam") == ("telur", "ayam")

    def test_trailing_comma(self) -> None:
        assert tokenize("telur, ayam,") == ("telur", "ayam")

    def test_split_on_newline(self) -> None:
        assert tokenize("telur\nayam") == ("telur", "ayam")

    def test_mixed_separator(self) -> None:
        assert tokenize("telur,\nayam\n, wortel") == ("telur", "ayam", "wortel")

    def test_collapse_inner_whitespace(self) -> None:
        assert tokenize("chicken   breast") == ("chicken breast",)

    def test_tab_treated_as_whitespace(self) -> None:
        assert tokenize("chicken\tbreast") == ("chicken breast",)

    def test_accepts_list_input(self) -> None:
        """Payload API berupa array — setiap elemen tetap di-tokenize."""
        assert tokenize(["telur", "ayam"]) == ("telur", "ayam")

    def test_list_element_may_contain_comma(self) -> None:
        assert tokenize(["telur, ayam", "wortel"]) == ("telur", "ayam", "wortel")

    def test_list_with_empty_elements(self) -> None:
        assert tokenize(["telur", "", "  ", "ayam"]) == ("telur", "ayam")

    def test_non_string_element_ignored(self) -> None:
        """Guard: validasi tipe adalah tugas schema, normalizer tidak boleh crash."""
        assert tokenize(["telur", None, 42, "ayam"]) == ("telur", "ayam")  # type: ignore[list-item]

    def test_duplicates_are_preserved_at_this_stage(self) -> None:
        """Dedupe terjadi setelah lookup, bukan di tokenize."""
        assert tokenize("telur, telur") == ("telur", "telur")

    def test_returns_tuple(self) -> None:
        assert isinstance(tokenize("telur"), tuple)
