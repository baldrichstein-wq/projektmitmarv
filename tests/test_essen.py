import io

from tests.conftest import auth_header, login_als


class TestEssenHTML:
    def _login_als_benutzer(self, client):
        login_als(client, "user@test.de", "user123")

    def _login_als_admin(self, client):
        login_als(client, "admin@test.de", "admin123")

    def test_essen_liste_gast_redirect(self, client):
        resp = client.get("/foods", follow_redirects=True)
        assert "anmelden" in resp.get_data(as_text=True).lower()

    def test_essen_liste_angemeldet(self, client):
        self._login_als_benutzer(client)
        resp = client.get("/foods")
        assert resp.status_code == 200
        assert "Test-Essen" in resp.get_data(as_text=True)

    def test_essen_hinzufuegen(self, client):
        self._login_als_benutzer(client)
        resp = client.post(
            "/foods",
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
        resp = client.post(f"/foods/{essen_id}/delete", follow_redirects=True)
        assert "Nur Administratoren" in resp.get_data(as_text=True)

    def test_essen_loeschen_als_admin(self, client, db):
        from app.models.essen import Essen

        self._login_als_admin(client)
        essen_id = Essen.query.first().id
        resp = client.post(f"/foods/{essen_id}/delete", follow_redirects=True)
        assert resp.status_code == 200

    def test_essen_bearbeiten(self, client, db):
        from app.models.essen import Essen

        self._login_als_benutzer(client)
        essen_id = Essen.query.first().id
        resp = client.post(
            f"/foods/{essen_id}/edit",
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

    def test_essen_export_json(self, client):
        self._login_als_admin(client)
        resp = client.get("/foods/export")
        assert resp.status_code == 200
        assert resp.mimetype == "application/json"
        assert "Test-Essen" in resp.get_data(as_text=True)

    def test_essen_import_json(self, client, db):
        from app.models.essen import Essen

        self._login_als_admin(client)
        payload = (
            '[{"name":"Import-Gericht","personenanzahl":3,"zutaten":["A","B"],'
            '"beschreibung":"Importiert","kochanweisung":"Kochen","kochzeit":25}]'
        )
        resp = client.post(
            "/foods/import",
            data={"json_file": (io.BytesIO(payload.encode("utf-8")), "essen.json")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert Essen.query.filter_by(name="Import-Gericht").first() is not None

    def test_essen_export_json_nur_admin(self, client):
        self._login_als_benutzer(client)
        resp = client.get("/foods/export", follow_redirects=True)
        assert resp.status_code == 200
        assert "Nur Administratoren dürfen Rezepte exportieren" in resp.get_data(
            as_text=True
        )

    def test_essen_import_json_nur_admin(self, client, db):
        from app.models.essen import Essen

        vorher = Essen.query.count()
        self._login_als_benutzer(client)
        payload = '[{"name":"Nicht-erlaubt"}]'
        resp = client.post(
            "/foods/import",
            data={"json_file": (io.BytesIO(payload.encode("utf-8")), "essen.json")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Nur Administratoren dürfen Rezepte importieren" in resp.get_data(
            as_text=True
        )
        assert Essen.query.count() == vorher

    def test_essen_import_additiv(self, client, db):
        from app.models.essen import Essen

        vorher = Essen.query.count()
        self._login_als_admin(client)
        payload = (
            '[{"name":"Zusatz-Gericht","personenanzahl":2,"zutaten":["Zutat"]'
            ',"beschreibung":"Neu","kochanweisung":"Kochen","kochzeit":20}]'
        )
        resp = client.post(
            "/foods/import",
            data={"json_file": (io.BytesIO(payload.encode("utf-8")), "essen.json")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert Essen.query.count() == vorher + 1

    def test_essen_import_mit_clear(self, client, db):
        from app.models.essen import Essen

        self._login_als_admin(client)
        payload = (
            '[{"name":"Nur-Dieses-Gericht","personenanzahl":1,"zutaten":["X"]'
            ',"beschreibung":"Einzig","kochanweisung":"Backen","kochzeit":30}]'
        )
        resp = client.post(
            "/foods/import",
            data={
                "json_file": (io.BytesIO(payload.encode("utf-8")), "essen.json"),
                "clear_table": "on",
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Bestehende Rezepte wurden gelöscht" in resp.get_data(as_text=True)
        assert Essen.query.count() == 1
        assert Essen.query.first().name == "Nur-Dieses-Gericht"


class TestEssenAPI:
    def test_api_essen_liste(self, client, admin_token):
        resp = client.get("/api/v1/foods/", headers=auth_header(admin_token))
        assert resp.status_code == 200
        daten = resp.get_json()
        assert isinstance(daten, list)
        assert len(daten) >= 1

    def test_api_essen_ohne_token(self, client):
        resp = client.get("/api/v1/foods/")
        assert resp.status_code == 401

    def test_api_essen_anlegen(self, client, user_token):
        resp = client.post(
            "/api/v1/foods/",
            json={
                "name": "API Gericht",
                "personenanzahl": 2,
                "zutaten": ["100g Mehl"],
                "beschreibung": "Test",
                "kochzeit": 10,
            },
            headers=auth_header(user_token),
        )
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "API Gericht"

    def test_api_essen_detail(self, client, admin_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.get(f"/api/v1/foods/{essen_id}", headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_api_essen_aktualisieren(self, client, user_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.put(
            f"/api/v1/foods/{essen_id}",
            json={"name": "Aktualisiert", "personenanzahl": 4},
            headers=auth_header(user_token),
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Aktualisiert"

    def test_api_essen_loeschen_als_admin(self, client, admin_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.delete(
            f"/api/v1/foods/{essen_id}", headers=auth_header(admin_token)
        )
        assert resp.status_code == 204

    def test_api_essen_loeschen_kein_admin(self, client, user_token, db):
        from app.models.essen import Essen

        essen_id = Essen.query.first().id
        resp = client.delete(
            f"/api/v1/foods/{essen_id}", headers=auth_header(user_token)
        )
        assert resp.status_code == 403
