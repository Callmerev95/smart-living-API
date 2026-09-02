"""Normalisasi input bahan dari user menjadi canonical name.

Deterministik dan tanpa LLM (`docs/technical-architecture.md` §7). Pipeline lengkap
ada di `docs/content-schema.md` §A.4.1:

    raw -> split -> trim -> lowercase -> collapse whitespace
        -> strip kuantitas -> lookup -> (canonical | unknown) -> dedupe

Normalizer menerima alias map lewat constructor, bukan membaca file sendiri, sehingga
bisa diuji tanpa dataset dan tetap O(1) per token.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

# Satuan yang dibuang bila muncul setelah angka (`docs/content-schema.md` §A.4.2).
QUANTITY_UNITS = (
    "gr",
    "gram",
    "kg",
    "ml",
    "l",
    "liter",
    "sdm",
    "sdt",
    "buah",
    "butir",
    "siung",
    "lembar",
    "batang",
    "ekor",
    "potong",
    "ikat",
    "bungkus",
    "pcs",
    "pieces",
)

# Angka di awal token: integer, desimal (1.5 / 1,5), atau pecahan (1/2).
_NUMBER = r"\d+(?:[.,]\d+)?(?:/\d+)?"

# Prefix kuantitas = angka + satuan opsional. Satuan boleh menempel ("250ml").
_QUANTITY_PREFIX = re.compile(
    rf"^{_NUMBER}\s*(?:(?:{'|'.join(QUANTITY_UNITS)})(?![a-z]))?\s*",
)

_WHITESPACE = re.compile(r"\s+")
_SPLIT_ON = re.compile(r"[,\n]")

# Kata yang berakhiran -es hanya di-strip bila didahului pola berikut (tomatoes -> tomato).
_ES_PLURAL = re.compile(r"(?:o|s|x|ch|sh)es$")


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    """Hasil normalisasi satu request.

    Attributes:
        raw: Token asli setelah trim + lowercase, sebelum lookup. Dipakai untuk
            menampilkan mapping `telur -> Telur` di frontend
            (Contract Delta v1.1 — `docs/content-schema.md` §A.9 Delta 3).
        canonical: Canonical name yang dikenali, sudah dedupe, urutan kemunculan
            pertama dipertahankan.
        unknown: Token di luar kamus. Dikembalikan ke client dengan HTTP 200
            (Delta 2), bukan dijadikan error.
    """

    raw: tuple[str, ...]
    canonical: tuple[str, ...]
    unknown: tuple[str, ...]


def tokenize(raw: str | Iterable[str]) -> tuple[str, ...]:
    """Pecah input menjadi token bersih (pipeline langkah 1-4).

    Menerima string (`"telur, ayam"`) maupun iterable string (payload API berupa
    array). Token kosong dibuang.
    """
    parts: list[str] = []
    chunks = [raw] if isinstance(raw, str) else list(raw)

    for chunk in chunks:
        if not isinstance(chunk, str):
            continue
        for piece in _SPLIT_ON.split(chunk):
            cleaned = _WHITESPACE.sub(" ", piece).strip().lower()
            if cleaned:
                parts.append(cleaned)

    return tuple(parts)


def strip_quantity(token: str) -> str:
    """Buang prefix angka dan satuan (pipeline langkah 5).

    Kuantitas hanya dibuang, TIDAK disimpan — kuantitas out of scope MVP
    (`docs/content-schema.md` §A.3.3).

    Hanya prefix yang disentuh: `"cabai 2 warna"` tetap utuh.
    """
    stripped = _QUANTITY_PREFIX.sub("", token, count=1).strip()
    # Jangan sampai token habis total (mis. input "2 kg" tanpa nama bahan).
    return stripped or token


def strip_plural(token: str) -> str:
    """Buang sufiks plural Inggris sederhana (pipeline langkah 6).

    Fallback ringan — plural yang penting tetap wajib ditulis eksplisit di `aliases`.
    Aturan ini hanya jaring pengaman.
    """
    if _ES_PLURAL.search(token):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


class IngredientNormalizer:
    """Ubah input bebas user menjadi canonical ingredient name."""

    def __init__(self, alias_map: Mapping[str, str]) -> None:
        """Args:
        alias_map: Peta `alias -> canonical`, termasuk canonical ke dirinya
            sendiri. Berasal dari `IngredientRepository.get_alias_map()`.
        """
        self._alias_map = dict(alias_map)

    def normalize(self, raw: str | Iterable[str]) -> NormalizationResult:
        """Jalankan pipeline lengkap `docs/content-schema.md` §A.4.1."""
        tokens = tokenize(raw)

        canonical: list[str] = []
        unknown: list[str] = []
        seen_canonical: set[str] = set()
        seen_unknown: set[str] = set()

        for token in tokens:
            resolved = self._lookup(token)

            if resolved is None:
                if token not in seen_unknown:
                    seen_unknown.add(token)
                    unknown.append(token)
                continue

            if resolved not in seen_canonical:
                seen_canonical.add(resolved)
                canonical.append(resolved)

        return NormalizationResult(
            raw=tokens,
            canonical=tuple(canonical),
            unknown=tuple(unknown),
        )

    def _lookup(self, token: str) -> str | None:
        """Cari canonical name untuk satu token (pipeline langkah 7).

        Urutan pencarian `docs/content-schema.md` §A.4.4: exact match, lalu setelah
        strip kuantitas, lalu setelah strip plural. Tidak ada fuzzy match — input tak
        dikenal tidak boleh dipetakan sembarangan.
        """
        if token in self._alias_map:
            return self._alias_map[token]

        without_quantity = strip_quantity(token)
        if without_quantity != token and without_quantity in self._alias_map:
            return self._alias_map[without_quantity]

        singular = strip_plural(without_quantity)
        if singular != without_quantity and singular in self._alias_map:
            return self._alias_map[singular]

        return None
