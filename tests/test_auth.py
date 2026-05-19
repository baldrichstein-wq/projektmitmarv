from datetime import timedelta

from flask_jwt_extended import create_access_token


class TestAnmeldung:
    def test_anmeldung_gueltig(self, client):
        resp = client.post(
            "/login",
            data={"email": "admin@test.de", "password": "admin123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_anmeldung_ungueltig(self, client):
        resp = client.post(
            "/login",
            data={"email": "admin@test.de", "password": "falsch"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Ungültige Anmeldedaten" in resp.get_data(as_text=True)

    def test_anmeldung_unbekannte_email(self, client):
        resp = client.post(
            "/login",
            data={"email": "unbekannt@test.de", "password": "irgendwas"},
            follow_redirects=True,
        )
        assert "Ungültige Anmeldedaten" in resp.get_data(as_text=True)


class TestRegistrierung:
    def test_registrierung_gueltig(self, client):
        resp = client.post(
            "/register",
            data={"name": "Neu", "email": "neu@test.de", "password": "test123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Registrierung erfolgreich" in resp.get_data(as_text=True)

    def test_registrierung_doppelte_email(self, client):
        resp = client.post(
            "/register",
            data={"name": "Doppelt", "email": "admin@test.de", "password": "test123"},
            follow_redirects=True,
        )
        assert "bereits registriert" in resp.get_data(as_text=True)

    def test_registrierung_leere_felder(self, client):
        resp = client.post(
            "/register",
            data={"name": "", "email": "", "password": ""},
            follow_redirects=True,
        )
        assert "Bitte alle Felder ausfüllen" in resp.get_data(as_text=True)


class TestAbmeldung:
    def test_abmeldung_redirect(self, client):
        client.post("/login", data={"email": "admin@test.de", "password": "admin123"})
        resp = client.get("/logout", follow_redirects=True)
        assert resp.status_code == 200
        assert "Erfolgreich abgemeldet" in resp.get_data(as_text=True)


class TestRollenzugriff:
    def test_benutzer_verwaltung_nur_admin(self, client):
        resp = client.get("/users", follow_redirects=True)
        assert "Zugriff verweigert" in resp.get_data(as_text=True)


class TestUngueltigerToken:
    def test_expired_cookie_redirected_to_login(self, client, app):
        with app.app_context():
            expired_token = create_access_token(
                identity="admin@test.de",
                additional_claims={"rolle": "admin", "name": "Admin"},
                expires_delta=timedelta(seconds=-1),
            )

        client.set_cookie("access_token_cookie", expired_token)
        resp = client.get("/wines", follow_redirects=True)
        body = resp.get_data(as_text=True)

        assert resp.status_code == 200
        assert "Bitte melde dich erneut an" in body
        assert "Anmeldung" in body

    def test_invalid_cookie_api_returns_401_json(self, client):
        client.set_cookie("access_token_cookie", "kaputter.token.wert")
        resp = client.get("/api/v1/foods/")

        assert resp.status_code == 422
        assert resp.is_json
        assert "msg" in resp.get_json()
