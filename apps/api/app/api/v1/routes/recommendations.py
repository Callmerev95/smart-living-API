"""Endpoint rekomendasi resep.

Route tipis: request tervalidasi -> service -> mapper -> response
(`docs/component-architecture.md` §35). Tidak ada perhitungan skor di sini.
"""

from fastapi import APIRouter, status

from app.api.v1.deps import RecommendationServiceDep
from app.schemas.error import ErrorResponse
from app.schemas.mappers import to_recommendation_response
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter(tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cari resep dari bahan yang dimiliki",
    description=(
        "Menormalisasi bahan yang dimasukkan user, mencocokkannya dengan dataset resep, "
        "lalu mengembalikan hasil terurut dari yang paling cocok.\n\n"
        "Perilaku penting:\n"
        "- Bahan pokok (garam, minyak, air, lada, gula) dianggap selalu tersedia sehingga "
        "tidak menurunkan persentase kecocokan.\n"
        "- Bahan di luar kamus dikembalikan lewat `unknownIngredients` dengan status 200, "
        "bukan sebagai error.\n"
        "- `query.raw` dan `query.ingredients` memperlihatkan hasil normalisasi agar client "
        "bisa menampilkan pemetaan seperti `telur` menjadi `egg`."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Daftar bahan tidak valid."},
        422: {"model": ErrorResponse, "description": "Struktur request tidak valid."},
        500: {"model": ErrorResponse, "description": "Kesalahan tak terduga di server."},
    },
)
def recommend(
    payload: RecommendationRequest,
    service: RecommendationServiceDep,
) -> RecommendationResponse:
    result = service.recommend(payload.ingredients, payload.limit)
    return to_recommendation_response(result)
