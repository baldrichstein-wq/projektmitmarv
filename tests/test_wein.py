from tests.conftest import auth_header, login_als


class TestWeinHTML:
    def _login_als_benutzer(self, client):
        login_als(client, "benutzer@test.de", "benutzer123")

    def _login_als_admin(self, client):
        login_als(client, "admin@test.de", "admin123")

    def test_wein_liste_gast_redirect(self, client):
        resp = client.get("/wein", follow_redirects=True)
        assert "anmelden" in resp.get_data(as_text=True).lower()

    def test_wein_liste_angemeldet(self, client):
        self._login_als_benutzer(client)
        resp = client.get("/wein")
        assert resp.status_code == 200
        assert "Test-Wein" in resp.get_data(as_text=True)

    def test_wein_hinzufuegen(self, client):
        self._login_als_benutzer(client)
        resp = client.post(
            "/wein",
            data={
                "name": "Neuer Wein",
                "liter": "5",
                "ingredients": "1kg Trauben, 500g Zucker",
                "description": "Sehr gut",
                "brewing_instructions": "Alles mischen",
                "brewing_time": "8",
                "alcohol_content": "12.5",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Neuer Wein" in resp.get_data(as_text=True)

    def test_wein_loeschen_nur_admin(self, client, db):
        from app.models.wein import Wein

        self._login_als_benutzer(client)
        wein_id = Wein.query.first().id
        resp = client.post(f"/wein/loeschen/{wein_id}", follow_redirects=True)
        assert "Nur Administratoren" in resp.get_data(as_text=True)

    def test_wein_loeschen_als_admin(self, client, db):
        from app.models.wein import Wein

        self._login_als_admin(client)
        wein_id = Wein.query.first().id
        resp = client.post(f"/wein/loeschen/{wein_id}", follow_redirects=True)
        assert resp.status_code == 200


class TestWeinAPI:
    def test_api_wein_liste(self, client, admin_token):
        resp = client.get("/api/v1/wein/", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_api_wein_ohne_token(self, client):
        resp = client.get("/api/v1/wein/")
        assert resp.status_code == 401

    def test_api_wein_anlegen(self, client, benutzer_token):
        resp = client.post(
            "/api/v1/wein/",
            json={
                "name": "API Wein",
                "liter": 5.0,
                "zutaten": ["1kg Trauben"],
                "brauzeit": 6,
                "alkoholgehalt": 11.5,
            },
            headers=auth_header(benutzer_token),
        )
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "API Wein"

    def test_api_wein_loeschen_kein_admin(self, client, benutzer_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.delete(f"/api/v1/wein/{wein_id}", headers=auth_header(benutzer_token))
        assert resp.status_code == 403

    def test_api_wein_loeschen_als_admin(self, client, admin_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.delete(f"/api/v1/wein/{wein_id}", headers=auth_header(admin_token))
        assert resp.status_code == 204
