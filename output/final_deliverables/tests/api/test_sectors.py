from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_sector_it():

    response = client.get("/api/v1/sectors/Information Technology/companies")

    assert response.status_code == 200

    companies = response.json()

    for row in companies:
        assert row["broad_sector"] == "Information Technology"


def test_invalid_sector():

    response = client.get("/api/v1/sectors/INVALID/companies")

    assert response.status_code == 404
