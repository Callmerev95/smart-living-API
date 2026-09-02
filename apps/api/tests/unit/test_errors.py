"""Test untuk error domain dan schema error."""

import pytest

from app.core.errors import (
    AppError,
    ErrorCode,
    IngredientNotFoundError,
    InvalidIngredientsError,
    RecipeNotFoundError,
)
from app.schemas.error import ErrorDetail, ErrorResponse


class TestErrorCode:
    def test_five_codes_defined(self) -> None:
        """docs/content-schema.md §A.10.5 mendefinisikan 5 kode."""
        assert {c.value for c in ErrorCode} == {
            "INVALID_INGREDIENTS",
            "VALIDATION_ERROR",
            "RECIPE_NOT_FOUND",
            "INGREDIENT_NOT_FOUND",
            "INTERNAL_ERROR",
        }

    def test_is_str_enum(self) -> None:
        assert ErrorCode.INVALID_INGREDIENTS == "INVALID_INGREDIENTS"


class TestAppError:
    def test_default_is_internal_error(self) -> None:
        error = AppError("boom")
        assert error.code is ErrorCode.INTERNAL_ERROR
        assert error.status_code == 500
        assert error.message == "boom"
        assert error.details is None

    def test_details_carried(self) -> None:
        error = AppError("boom", details={"field": "x"})
        assert error.details == {"field": "x"}

    def test_is_exception(self) -> None:
        with pytest.raises(AppError):
            raise AppError("boom")

    def test_does_not_import_fastapi(self) -> None:
        """Exception domain tidak boleh tahu HTTP framework."""
        from pathlib import Path

        source = (Path(__file__).resolve().parents[2] / "app" / "core" / "errors.py").read_text()
        assert "fastapi" not in source


class TestSpecificErrors:
    def test_invalid_ingredients_maps_to_400(self) -> None:
        error = InvalidIngredientsError("kosong")
        assert error.code is ErrorCode.INVALID_INGREDIENTS
        assert error.status_code == 400

    def test_recipe_not_found_maps_to_404(self) -> None:
        error = RecipeNotFoundError("recipe_999")
        assert error.code is ErrorCode.RECIPE_NOT_FOUND
        assert error.status_code == 404
        assert error.recipe_id == "recipe_999"
        assert "recipe_999" in error.message

    def test_ingredient_not_found_maps_to_404(self) -> None:
        error = IngredientNotFoundError("kangkung")
        assert error.code is ErrorCode.INGREDIENT_NOT_FOUND
        assert error.status_code == 404

    def test_all_inherit_app_error(self) -> None:
        for error_cls in (InvalidIngredientsError, RecipeNotFoundError, IngredientNotFoundError):
            assert issubclass(error_cls, AppError)


class TestErrorSchema:
    def test_structure_matches_contract(self) -> None:
        response = ErrorResponse(
            error=ErrorDetail(code="INVALID_INGREDIENTS", message="Bahan kosong.")
        )
        payload = response.model_dump(by_alias=True)
        assert payload == {
            "error": {
                "code": "INVALID_INGREDIENTS",
                "message": "Bahan kosong.",
                "details": None,
            }
        }

    def test_details_can_hold_list(self) -> None:
        response = ErrorResponse(
            error=ErrorDetail(code="VALIDATION_ERROR", message="x", details=[{"field": "limit"}])
        )
        assert response.error.details == [{"field": "limit"}]

    def test_details_defaults_to_none(self) -> None:
        assert ErrorDetail(code="X", message="y").details is None
