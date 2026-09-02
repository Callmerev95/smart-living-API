"""Orchestration layer untuk rekomendasi resep.

Menyusun urutan operasi `docs/content-schema.md` §A.6:

    normalize -> get recipes -> score -> filter threshold -> rank -> limit

Service tidak menghitung skor sendiri (delegasi ke `domain/matching`), tidak tahu
format JSON (hanya bicara ke interface repository), dan tidak tahu HTTP
(`docs/component-architecture.md` §15, `AGENTS.md` §4).
"""

from collections.abc import Iterable
from dataclasses import dataclass

from app.core.config import Settings
from app.domain.matching.engine import match_recipes
from app.domain.matching.ranking import apply_limit, filter_by_threshold, rank
from app.domain.models.match_result import MatchResult
from app.repositories.base import IngredientRepository, RecipeRepository
from app.services.ingredient_normalizer import IngredientNormalizer


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Hasil rekomendasi pada level domain — belum menjadi response HTTP.

    Attributes:
        raw: Token input asli setelah trim + lowercase (Delta 3).
        canonical: Canonical name hasil normalisasi, sudah dedupe (Delta 3).
        unknown: Bahan di luar kamus (Delta 2). Bukan error.
        results: Hasil yang sudah difilter, diurutkan, dan dibatasi.
        limit: Limit yang benar-benar dipakai setelah clamping.
        threshold: Ambang relevansi yang dipakai — dikembalikan untuk transparansi.
    """

    raw: tuple[str, ...]
    canonical: tuple[str, ...]
    unknown: tuple[str, ...]
    results: tuple[MatchResult, ...]
    limit: int
    threshold: int


class RecommendationService:
    """Use case utama: dari bahan user menjadi daftar resep terurut."""

    def __init__(
        self,
        normalizer: IngredientNormalizer,
        recipe_repository: RecipeRepository,
        ingredient_repository: IngredientRepository,
        settings: Settings,
    ) -> None:
        self._normalizer = normalizer
        self._recipe_repository = recipe_repository
        self._ingredient_repository = ingredient_repository
        self._settings = settings

    def recommend(
        self,
        ingredients: str | Iterable[str],
        limit: int | None = None,
    ) -> RecommendationResult:
        """Hasilkan rekomendasi resep.

        Args:
            ingredients: Input bahan mentah dari user.
            limit: Jumlah maksimum hasil. `None` memakai `settings.default_limit`.
                Nilai di luar rentang di-clamp ke `1..settings.max_limit` — validasi
                yang menolak input adalah tanggung jawab API layer.

        Returns:
            `RecommendationResult` berisi hasil terurut plus data normalisasi untuk
            Contract Delta v1.1.
        """
        effective_limit = self._resolve_limit(limit)
        threshold = self._settings.min_match_threshold

        normalization = self._normalizer.normalize(ingredients)

        scored = match_recipes(
            normalization.canonical,
            self._recipe_repository.get_all(),
            self._ingredient_repository.get_staple_names(),
        )

        # Urutan wajib: filter dulu, baru sort, baru limit — agar slot limit tidak
        # terpakai hasil di bawah threshold (docs/content-schema.md §A.6).
        relevant = filter_by_threshold(scored, threshold)
        ranked = rank(relevant)
        limited = apply_limit(ranked, effective_limit)

        return RecommendationResult(
            raw=normalization.raw,
            canonical=normalization.canonical,
            unknown=normalization.unknown,
            results=limited,
            limit=effective_limit,
            threshold=threshold,
        )

    def _resolve_limit(self, limit: int | None) -> int:
        if limit is None:
            return self._settings.default_limit
        return max(1, min(limit, self._settings.max_limit))
