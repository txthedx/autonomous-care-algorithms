"""Tests for the REST API.

These run only when the optional `[api]` dependencies are installed; otherwise
they are skipped (CI installs only `.[dev]`). The underlying engine logic is
already covered by the registry and dispatch test suites.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from engine.api import create_app  # noqa: E402

_HEART = dict(
    history="moderately_suspicious", ecg="normal", age_years=58,
    hypertension=True, hypercholesterolemia=True, diabetes_mellitus=False,
    current_or_recent_smoking=False, family_history_of_cad=False,
    obesity_bmi_over_30=False, history_of_atherosclerotic_disease=False,
    troponin="at_or_below_normal_limit",
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


class TestCatalogEndpoints:
    def test_root_has_disclaimer(self, client: TestClient) -> None:
        body = client.get("/").json()
        assert body["conditions"] >= 24
        assert "not a medical device" in body["disclaimer"].lower()

    def test_list_conditions(self, client: TestClient) -> None:
        resp = client.get("/conditions")
        assert resp.status_code == 200
        assert any(c["key"] == "heart" for c in resp.json())

    def test_presentations(self, client: TestClient) -> None:
        assert "chest pain" in client.get("/presentations").json()

    def test_schema(self, client: TestClient) -> None:
        schema = client.get("/conditions/heart/schema").json()
        assert schema["type"] == "object" and schema["properties"]

    def test_describe(self, client: TestClient) -> None:
        assert client.get("/conditions/heart").json()["key"] == "heart"

    def test_unknown_condition_404(self, client: TestClient) -> None:
        assert client.get("/conditions/nope").status_code == 404
        assert client.get("/conditions/nope/schema").status_code == 404


class TestRunEndpoint:
    def test_run_success(self, client: TestClient) -> None:
        resp = client.post("/conditions/heart/run", json=_HEART)
        assert resp.status_code == 200
        body = resp.json()
        assert body["result"]["score"] == 3
        assert "not a medical device" in body["disclaimer"].lower()

    def test_run_missing_inputs_422(self, client: TestClient) -> None:
        resp = client.post("/conditions/kdigo/run", json={"egfr_ml_min_1_73m2": 50.0})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert "acr_mg_per_mmol" in detail["missing_inputs"]

    def test_run_out_of_range_422(self, client: TestClient) -> None:
        resp = client.post("/conditions/kdigo/run", json={
            "egfr_ml_min_1_73m2": -1.0, "acr_mg_per_mmol": 1.0,
            "persistent_over_3_months": True,
        })
        assert resp.status_code == 422

    def test_run_unknown_condition_404(self, client: TestClient) -> None:
        assert client.post("/conditions/nope/run", json={}).status_code == 404


class TestDispatchEndpoints:
    def test_suggest(self, client: TestClient) -> None:
        resp = client.post("/suggest",
                           json={"features": _HEART, "presentation": "chest pain"})
        assert resp.status_code == 200
        heart = next(r for r in resp.json() if r["key"] == "heart")
        assert heart["runnable"] is True

    def test_run_applicable(self, client: TestClient) -> None:
        resp = client.post("/run-applicable",
                           json={"features": _HEART, "presentation": "chest pain"})
        assert resp.status_code == 200
        body = resp.json()
        assert any(r["key"] == "heart" for r in body["applicable"])
        assert "disclaimer" in body

    def test_openapi_available(self, client: TestClient) -> None:
        spec = client.get("/openapi.json").json()
        assert "/conditions/{condition}/run" in spec["paths"]
