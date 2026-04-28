def test_health_returns_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


def test_dashboard_root_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower()


def test_pipeline_json_shape(client):
    resp = client.get("/api/pipeline")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["live"] is True
    assert "bronze" in data and "silver" in data


def test_kpis_returns_numbers(client):
    resp = client.get("/api/kpis")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_events" in data
    assert "artisans" in data


def test_manifest_is_served(client):
    resp = client.get("/manifest.webmanifest")
    assert resp.status_code == 200


def test_chat_returns_reply(client):
    resp = client.post(
        "/api/chat",
        json={"message": "What is the price?", "product": "Test Product", "artisan": "Zainab Bibi"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reply" in data
    assert "artisan" in data
    assert "timestamp" in data
    assert "price" in data["reply"].lower() or "clearly" in data["reply"].lower()
