from tests.conftest import auth_header


class TestBenutzerHTML:
    def _login_als_admin(self, client):
        with client.session_transaction() as sess:
            sess["user_email"] = "admin@test.de"
            sess["user_role"] = "admin"

    def test_benutzer_verwaltung_kein_zugriff_als_gast(self, client):
        resp = client.get("/benutzer", follow_redirects=True)
        assert "Zugriff verweigert" in resp.get_data(as_text=True)

    def test_benutzer_verwaltung_als_admin(self, client):
        self._login_als_admin(client)
        resp = client.get("/benutzer")
        assert resp.status_code == 200
        assert "admin@test.de" in resp.get_data(as_text=True)

    def test_benutzer_anlegen(self, client):
        self._login_als_admin(client)
        resp = client.post(
            "/benutzer",
            data={"name": "Neuer", "email": "neuer@test.de", "password": "pw123"},
            follow_redirects=True,
        )
        assert "Neuer" in resp.get_data(as_text=True)

    def test_benutzer_anlegen_doppelte_email(self, client):
        self._login_als_admin(client)
        resp = client.post(
            "/benutzer",
            data={"name": "Doppelt", "email": "admin@test.de", "password": "pw123"},
            follow_redirects=True,
        )
        assert "bereits vergeben" in resp.get_data(as_text=True)

    def test_rolle_aendern(self, client, db):
        from app.models.benutzer import Benutzer

        self._login_als_admin(client)
        benutzer = Benutzer.query.filter_by(email="benutzer@test.de").first()
        resp = client.post(
            f"/benutzer/rolle_aendern/{benutzer.id}",
            data={"rolle": "gast"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        db.session.refresh(benutzer)
        assert benutzer.rolle == "gast"

    def test_rolle_aendern_ungueltige_rolle(self, client, db):
        from app.models.benutzer import Benutzer

        self._login_als_admin(client)
        benutzer = Benutzer.query.filter_by(email="benutzer@test.de").first()
        resp = client.post(
            f"/benutzer/rolle_aendern/{benutzer.id}",
            data={"rolle": "superuser"},
            follow_redirects=True,
        )
        assert "Ungültige Rolle" in resp.get_data(as_text=True)


class TestBenutzerAPI:
    def test_api_benutzer_liste_als_admin(self, client, admin_token):
        resp = client.get("/api/v1/benutzer/", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_api_benutzer_liste_kein_admin(self, client, benutzer_token):
        resp = client.get("/api/v1/benutzer/", headers=auth_header(benutzer_token))
        assert resp.status_code == 403

    def test_api_rolle_aendern(self, client, admin_token, db):
        from app.models.benutzer import Benutzer

        benutzer = Benutzer.query.filter_by(email="benutzer@test.de").first()
        resp = client.put(
            f"/api/v1/benutzer/{benutzer.id}/rolle",
            json={"rolle": "gast"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        assert resp.get_json()["rolle"] == "gast"
