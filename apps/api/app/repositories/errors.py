"""Error yang muncul saat memuat dataset dari sumber data."""


class DatasetLoadError(RuntimeError):
    """Dataset tidak bisa dimuat atau strukturnya tidak sesuai kontrak.

    Dilempar saat inisialisasi repository (fail fast) — lebih baik server gagal
    start dengan pesan jelas daripada melayani request dengan dataset rusak.
    """
