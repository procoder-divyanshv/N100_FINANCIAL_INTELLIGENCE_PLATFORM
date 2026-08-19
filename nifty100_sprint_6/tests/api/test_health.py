from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "db_row_counts" in data

def test_get_companies():
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_company_not_found():
    response = client.get("/api/v1/companies/INVALID_TICKER_XYZ")
    assert response.status_code == 404