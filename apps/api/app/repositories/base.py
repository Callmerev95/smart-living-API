"""Interface repository — abstraksi akses data.

Service hanya bergantung pada interface ini, bukan pada format JSON. Ketika kelak
dataset pindah ke PostgreSQL, business logic tidak perlu berubah
(`docs/technical-architecture.md` §5.4, `docs/component-architecture.md` §20).

Repository TIDAK menentukan ranking atau scoring
(`docs/component-architecture.md` §25 Rule 5).
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping

from app.domain.models.ingredient import Ingredient
from app.domain.models.recipe import Recipe


class RecipeRepository(ABC):
    """Akses data resep."""

    @abstractmethod
    def get_all(self) -> tuple[Recipe, ...]:
        """Semua resep. Urutan harus stabil antar pemanggilan (determinisme)."""

    @abstractmethod
    def get_by_id(self, recipe_id: str) -> Recipe | None:
        """Satu resep berdasarkan id, atau `None` bila tidak ada.

        Sengaja mengembalikan `None` alih-alih raise: "tidak ditemukan" adalah
        kondisi normal yang diputuskan pemanggil (API layer memetakannya ke 404).
        """

    @abstractmethod
    def count(self) -> int:
        """Jumlah resep yang ter-load."""


class IngredientRepository(ABC):
    """Akses kamus bahan kanonik."""

    @abstractmethod
    def get_all(self) -> tuple[Ingredient, ...]:
        """Semua ingredient. Urutan stabil."""

    @abstractmethod
    def get_by_name(self, name: str) -> Ingredient | None:
        """Ingredient berdasarkan canonical name, atau `None`.

        Hanya menerima canonical name — alias diselesaikan lewat `get_alias_map()`.
        """

    @abstractmethod
    def get_alias_map(self) -> Mapping[str, str]:
        """Peta `alias -> canonical name`, termasuk canonical name ke dirinya sendiri.

        Normalizer bergantung pada abstraksi ini, bukan pada implementasi JSON,
        sehingga lookup tetap O(1) apa pun sumber datanya
        (`docs/content-schema.md` §A.4.4).
        """

    @abstractmethod
    def get_staple_names(self) -> frozenset[str]:
        """Canonical name bahan dengan `staple: true`.

        Dipakai matching engine untuk mengecualikan staple dari scoring
        (Contract Delta v1.1 — `docs/content-schema.md` §A.9 Delta 1).
        """

    @abstractmethod
    def count(self) -> int:
        """Jumlah ingredient yang ter-load."""
