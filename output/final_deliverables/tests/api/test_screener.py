from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_min_roe():

    response = client.get("/api/v1/screener?min_roe=15")

    assert response.status_code == 200

    rows = response.json()

    for row in rows:
        assert row["return_on_equity_pct"] >= 15


def test_invalid_parameter():

    response = client.get("/api/v1/screener?min_roe=-1")

    assert response.status_code == 400
