"""Smoke-Test: App startet und Home-Route antwortet mit 200."""
from app import create_app


def test_home_page_returns_200():
    app = create_app("testing")
    with app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == 200

