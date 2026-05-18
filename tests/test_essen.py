from tests.conftest import auth_header, login_als


class TestEssenHTML:
    def _login_als_benutzer(self, client):
        login_als(client, "benutzer@test.de", "benutzer123")

    def _login_als_admin(self, client):
        login_als(client, "admin@test.de", "admin123")

    def test_essen_liste_gast_redirect(self, client):
        resp = client.get("/essen", follow_redirects=True)
        assert "anmelden" in resp.get_data(as_text=True).lower()

    def test_essen_liste_angemeldet(self, client):
        self._login_als_benutzer(client)
        resp = client.get("/essen")
        assert resp.status_code == 200
        assert "Test-Essen" in resp.get_data(as_text=True)

    def test_essen_hinzufuegen(self, client):
        self._login_als_benutzer(client)
        resp = client.post(
            "/essen",
            data={
                "name": "Neues Gericht",
                "personenanzahl": "2",
                "ingredients": "100g Mehl, 2 Eier",
                "description": "Sehr lecker",
                "kochanweisung": "Alles mischen",
                "kochzeit": "30",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Neues Gericht" in resp.get_data(as_text=True)

    def test_essen_loeschen_nur_admin(self, client, db):
        from app.models.essen import Essen

        self._login_als_benutzer(client)
        essen_id = Essen.query.first().id
        resp = client.post(f"/essen/loeschen/{essen_id}", follow_redirects=True)
        assert "Nur Administratoren" in resp.get_data(as_text=True)

    def test_essen_loeschen_als_admin(self, client, db):
        from app.models.essen import Essen

        self._login_als_admin(client)
        essen_id = Essen.query.first().id
        resp = client.post(f"/essen/loeschen/{essen_id}", follow_redirects=True)
        assert resp.status_code == 200

    def test_essen_bearbeiten(self, client, db):
        from app.models.essen import Essen

        self._login_als_benutzer(client)
        essen_id = Essen.query.first().id
        resp = client.post(
            f"/essen/bearbeiten/{essen_id}",
            data={
                "name": "Geändertes Essen",
                "personenanzahl": "3",
                "ingredients": "200g Reis",
                "description": "Neu",
                "kochanweisung": "Kochen",
                "kochzeit": "15",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200


class TestEssenAPI:
    def test_api_essen_liste(self, client, admin_token):
        resp = client.get("/api/v1/essen/", headers=auth_header(admin_token))
        assert resp.status_code == 200
        daten = resp.get_json()
        assert isinstance(daten, list)
        assert len(daten) >= 1

    def test_api_essen_ohne_token(self, client):
        resp = client.get("/api/v1/essen/")
        assert resp.status_code == 401

    def test_api_essen_anlegen(self, client, benutzer_token):
        resp = client.post(
            "/api/v1/essen/",
            json={
                "name": "API Gericht",
                "personenanzahl": 2,
                "zutaten": ["100g Mehl"],
                "beschreibung": "Test",
                "kochzeit": 10,
            },
            headers=auth_header(benutzer_token),
        )
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "API Gericht"

    def test_api_essen_detail(self, client, admin_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.get(f"/api/v1/essen/{essen_id}", headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_api_essen_aktualisieren(self, client, benutzer_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.put(
            f"/api/v1/essen/{essen_id}",
            json={"name": "Aktualisiert", "personenanzahl": 4},
            headers=auth_header(benutzer_token),
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Aktualisiert"

    def test_api_essen_loeschen_als_admin(self, client, admin_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.delete(f"/api/v1/essen/{essen_id}", headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_api_essen_loeschen_kein_admin(self, client, benutzer_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.delete(f"/api/v1/essen/{essen_id}", headers=auth_header(benutzer_token))
        assert resp.status_code == 403
