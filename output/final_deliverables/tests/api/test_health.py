from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health():

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    tables = {
        "companies",
        "sectors",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "financial_ratios",
        "peer_groups",
        "documents",
        "analysis",
        "stock_prices",
    }

    assert tables == set(data["db_row_counts"].keys())
