"""Smoke-Test: App startet und Home-Route antwortet mit 200."""

from app import create_app


def test_home_page_returns_200():
    app = create_app("testing")
    with app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == 200


def test_webui_alias_routes_available():
    app = create_app("testing")
    with app.test_client() as client:
        assert client.get("/login").status_code == 200
        assert client.get("/register").status_code == 200
        assert client.get("/about").status_code == 200
        assert client.get("/search").status_code == 200


def test_search_finds_seeded_wine(client):
    resp = client.get("/search?q=trauben")
    assert resp.status_code == 200
    assert "Test-Wein" in resp.get_data(as_text=True)


def test_search_finds_seeded_food(client):
    resp = client.get("/search?q=nudeln")
    assert resp.status_code == 200
    assert "Test-Essen" in resp.get_data(as_text=True)
