"""Perhitungan match percentage — pure function.

Rumus: `docs/content-schema.md` §A.5.2 (dengan Contract Delta v1.1: staple sudah
dikecualikan dari denominator oleh pemanggil — fungsi ini hanya menerima angka).

Fungsi ini adalah pure function: input primitif, output integer, tanpa I/O dan
tanpa state.
"""


def calculate_match_percentage(matched: int, denominator: int) -> int:
    """Hitung persentase kecocokan dengan pembulatan half-up.

    Args:
        matched: Jumlah required non-staple yang user miliki (`|Rc ∩ U|`).
        denominator: Jumlah required non-staple resep (`|Rc|`). Staple TIDAK
            termasuk — itu ditangani di `engine.py` sebelum fungsi ini dipanggil.

    Returns:
        Integer 0-100. `0` bila denominator nol (guard divide-by-zero, bukan raise).

    Pembulatan half-up eksak: `2/3 -> 67`, `1/3 -> 33`, `1/2 -> 50`, `1/8 -> 13`.
    `round()` bawaan Python adalah banker's rounding (half-to-even) sehingga
    tidak dipakai — `round(12.5)` menghasilkan 12, bukan 13.
    """
    if denominator <= 0 or matched <= 0:
        return 0

    quotient, remainder = divmod(matched * 100, denominator)
    if 2 * remainder >= denominator:
        quotient += 1

    return min(quotient, 100)
