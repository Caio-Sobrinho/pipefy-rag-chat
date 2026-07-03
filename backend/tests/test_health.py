def test_health_check_returns_api_status(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["api"] == "running"
    assert data["redis"] in ["connected", "disconnected"]
    assert data["status"] in ["ok", "degraded"]