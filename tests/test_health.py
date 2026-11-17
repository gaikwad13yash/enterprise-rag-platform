from fastapi.testclient import TestClient

from enterprise_rag.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "Enterprise RAG Platform"


def test_readiness_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "connected",
    }


def test_openapi_documentation():
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
