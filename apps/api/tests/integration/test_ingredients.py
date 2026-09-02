"""Integration test untuk endpoint ingredients (`docs/content-schema.md` §A.10.3)."""

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


class TestListIngredients:
    def test_returns_200_with_full_dictionary(self) -> None:
        response = client.get("/api/v1/ingredients")
        assert response.status_code == 200
        payload = response.json()
        assert payload["meta"]["count"] == 94
        assert len(payload["ingredients"]) == 94

    def test_item_shape(self) -> None:
        item = client.get("/api/v1/ingredients").json()["ingredients"][0]
        assert set(item) == {"name", "displayName", "aliases", "category", "staple"}

    def test_meta_count_matches_array_length(self) -> None:
        payload = client.get("/api/v1/ingredients").json()
        assert payload["meta"]["count"] == len(payload["ingredients"])

    def test_staple_flag_present(self) -> None:
        payload = client.get("/api/v1/ingredients").json()
        staples = [i["name"] for i in payload["ingredients"] if i["staple"]]
        assert set(staples) == {"salt", "cooking_oil", "water", "pepper", "sugar"}

    def test_aliases_included_for_autocomplete(self) -> None:
        payload = client.get("/api/v1/ingredients").json()
        egg = next(i for i in payload["ingredients"] if i["name"] == "egg")
        assert "telur" in egg["aliases"]
        assert egg["displayName"] == "Telur"

    def test_order_is_stable_across_requests(self) -> None:
        first = client.get("/api/v1/ingredients").json()["ingredients"]
        second = client.get("/api/v1/ingredients").json()["ingredients"]
        assert [i["name"] for i in first] == [i["name"] for i in second]
