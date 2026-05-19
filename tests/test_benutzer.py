from tests.conftest import auth_header, login_als


class TestBenutzerHTML:
    def _login_als_admin(self, client):
        login_als(client, "admin@test.de", "admin123")

    def test_benutzer_verwaltung_kein_zugriff_als_gast(self, client):
        resp = client.get("/users", follow_redirects=True)
        assert "Zugriff verweigert" in resp.get_data(as_text=True)

    def test_benutzer_verwaltung_als_admin(self, client):
        self._login_als_admin(client)
        resp = client.get("/users")
        assert resp.status_code == 200
        assert "admin@test.de" in resp.get_data(as_text=True)

    def test_benutzer_anlegen(self, client):
        self._login_als_admin(client)
        resp = client.post(
            "/users",
            data={"name": "Neuer", "email": "neuer@test.de", "password": "pw123"},
            follow_redirects=True,
        )
        assert "Neuer" in resp.get_data(as_text=True)

    def test_benutzer_anlegen_doppelte_email(self, client):
        self._login_als_admin(client)
        resp = client.post(
            "/users",
            data={"name": "Doppelt", "email": "admin@test.de", "password": "pw123"},
            follow_redirects=True,
        )
        assert "bereits vergeben" in resp.get_data(as_text=True)

    def test_rolle_aendern(self, client, db):
        from app.models.benutzer import Benutzer

        self._login_als_admin(client)
        benutzer = Benutzer.query.filter_by(email="user@test.de").first()
        resp = client.post(
            f"/users/{benutzer.id}/role",
            data={"rolle": "gast"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        db.session.refresh(benutzer)
        assert benutzer.rolle == "gast"

    def test_rolle_aendern_ungueltige_rolle(self, client, db):
        from app.models.benutzer import Benutzer

        self._login_als_admin(client)
        benutzer = Benutzer.query.filter_by(email="user@test.de").first()
        resp = client.post(
            f"/users/{benutzer.id}/role",
            data={"rolle": "superuser"},
            follow_redirects=True,
        )
        assert "Ungültige Rolle" in resp.get_data(as_text=True)

    def test_benutzer_loeschen(self, client, db):
        from app.models.benutzer import Benutzer

        self._login_als_admin(client)
        benutzer = Benutzer.query.filter_by(email="user@test.de").first()

        resp = client.post(
            f"/users/{benutzer.id}/delete",
            follow_redirects=True,
        )

        assert resp.status_code == 200
        assert "wurde gelöscht" in resp.get_data(as_text=True)
        assert Benutzer.query.filter_by(email="user@test.de").first() is None

    def test_benutzer_kann_sich_nicht_selbst_loeschen(self, client, db):
        from app.models.benutzer import Benutzer

        self._login_als_admin(client)
        admin = Benutzer.query.filter_by(email="admin@test.de").first()

        resp = client.post(
            f"/users/{admin.id}/delete",
            follow_redirects=True,
        )

        assert resp.status_code == 200
        assert "nicht löschen" in resp.get_data(as_text=True)
        assert Benutzer.query.filter_by(email="admin@test.de").first() is not None


class TestBenutzerAPI:
    def test_api_benutzer_liste_als_admin(self, client, admin_token):
        resp = client.get("/api/v1/users/", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_api_benutzer_anlegen_als_admin(self, client, admin_token):
        resp = client.post(
            "/api/v1/users/",
            json={
                "name": "Neu API",
                "email": "neu.api@test.de",
                "password": "geheim123",
                "rolle": "user",
            },
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 201
        daten = resp.get_json()
        assert daten["email"] == "neu.api@test.de"
        assert daten["rolle"] == "user"
        assert "password" not in daten

    def test_api_benutzer_anlegen_kein_admin(self, client, user_token):
        resp = client.post(
            "/api/v1/users/",
            json={
                "name": "Verboten",
                "email": "verboten@test.de",
                "password": "geheim123",
            },
            headers=auth_header(user_token),
        )
        assert resp.status_code == 403

    def test_api_benutzer_anlegen_doppelte_email(self, client, admin_token):
        resp = client.post(
            "/api/v1/users/",
            json={
                "name": "Doppelt",
                "email": "admin@test.de",
                "password": "geheim123",
            },
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 409

    def test_api_benutzer_liste_kein_admin(self, client, user_token):
        resp = client.get("/api/v1/users/", headers=auth_header(user_token))
        assert resp.status_code == 403

    def test_api_rolle_aendern(self, client, admin_token, db):
        from app.models.benutzer import Benutzer

        benutzer = Benutzer.query.filter_by(email="user@test.de").first()
        resp = client.patch(
            f"/api/v1/users/{benutzer.id}",
            json={"rolle": "gast"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        assert resp.get_json()["rolle"] == "gast"

    def test_api_rolle_aendern_kein_admin(self, client, user_token):
        from app.models.benutzer import Benutzer

        admin = Benutzer.query.filter_by(email="admin@test.de").first()
        resp = client.patch(
            f"/api/v1/users/{admin.id}",
            json={"rolle": "gast"},
            headers=auth_header(user_token),
        )
        assert resp.status_code == 403

    def test_api_benutzer_loeschen_als_admin(self, client, admin_token):
        from app.models.benutzer import Benutzer

        benutzer = Benutzer.query.filter_by(email="user@test.de").first()
        resp = client.delete(
            f"/api/v1/users/{benutzer.id}",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 204
        assert Benutzer.query.filter_by(email="user@test.de").first() is None

    def test_api_benutzer_loeschen_kein_admin(self, client, user_token):
        from app.models.benutzer import Benutzer

        admin = Benutzer.query.filter_by(email="admin@test.de").first()
        resp = client.delete(
            f"/api/v1/users/{admin.id}",
            headers=auth_header(user_token),
        )
        assert resp.status_code == 403

    def test_api_benutzer_kann_sich_nicht_selbst_loeschen(self, client, admin_token):
        from app.models.benutzer import Benutzer

        admin = Benutzer.query.filter_by(email="admin@test.de").first()
        resp = client.delete(
            f"/api/v1/users/{admin.id}",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 403
