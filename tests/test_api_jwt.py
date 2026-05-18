from tests.conftest import auth_header


class TestJWTLogin:
    def test_login_gueltig(self, client):
        resp = client.post(
            "/api/v1/auth/login", json={"email": "admin@test.de", "password": "admin123"}
        )
        assert resp.status_code == 200
        daten = resp.get_json()
        assert "access_token" in daten
        assert "refresh_token" in daten

    def test_login_ungueltig(self, client):
        resp = client.post(
            "/api/v1/auth/login", json={"email": "admin@test.de", "password": "falsch"}
        )
        assert resp.status_code == 401

    def test_login_fehlende_felder(self, client):
        resp = client.post("/api/v1/auth/login", json={"email": "admin@test.de"})
        assert resp.status_code == 422

    def test_geschuetzte_route_ohne_token(self, client):
        resp = client.get("/api/v1/essen/")
        assert resp.status_code == 401

    def test_geschuetzte_route_mit_token(self, client, admin_token):
        resp = client.get("/api/v1/essen/", headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_token_refresh(self, client):
        resp = client.post(
            "/api/v1/auth/login", json={"email": "admin@test.de", "password": "admin123"}
        )
        refresh_token = resp.get_json()["refresh_token"]

        resp2 = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert resp2.status_code == 200
        assert "access_token" in resp2.get_json()

    def test_access_token_nicht_fuer_refresh(self, client, admin_token):
        # Access-Token darf nicht als Refresh-Token verwendet werden
        resp = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    def test_ungueltige_rolle_im_token(self, client, benutzer_token):
        # Benutzer-Token darf kein Admin-Endpunkt aufrufen
        resp = client.get("/api/v1/benutzer/", headers=auth_header(benutzer_token))
        assert resp.status_code == 403
