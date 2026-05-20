from fastapi.testclient import TestClient

from smc_ai.dashboard.app import create_app


def test_dashboard_home_returns_html():
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "Tableau de bord SMC AI" in response.text


def test_dashboard_health_returns_html():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert "Santé de la stratégie" in response.text
