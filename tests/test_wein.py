from tests.conftest import auth_header, login_als


class TestWeinHTML:
    def _login_als_user(self, client):
        login_als(client, "user@test.de", "user123")

    def _login_als_admin(self, client):
        login_als(client, "admin@test.de", "admin123")

    def test_wein_liste_gast_redirect(self, client):
        resp = client.get("/wines", follow_redirects=True)
        assert "anmelden" in resp.get_data(as_text=True).lower()

    def test_wein_liste_angemeldet(self, client):
        self._login_als_user(client)
        resp = client.get("/wines")
        assert resp.status_code == 200
        assert "Test-Wein" in resp.get_data(as_text=True)

    def test_wein_hinzufuegen(self, client):
        self._login_als_user(client)
        resp = client.post(
            "/wines",
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

        self._login_als_user(client)
        wein_id = Wein.query.first().id
        resp = client.post(f"/wines/{wein_id}/delete", follow_redirects=True)
        assert "Nur Administratoren" in resp.get_data(as_text=True)

    def test_wein_loeschen_als_admin(self, client, db):
        from app.models.wein import Wein

        self._login_als_admin(client)
        wein_id = Wein.query.first().id
        resp = client.post(f"/wines/{wein_id}/delete", follow_redirects=True)
        assert resp.status_code == 200

    def test_wein_bearbeiten_get(self, client, db):
        from app.models.wein import Wein

        self._login_als_user(client)
        wein_id = Wein.query.first().id
        resp = client.get(f"/wines/{wein_id}/edit")
        assert resp.status_code == 200
        assert "Test-Wein" in resp.get_data(as_text=True)

    def test_wein_bearbeiten_als_gast_redirect(self, client, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.get(f"/wines/{wein_id}/edit", follow_redirects=True)
        assert resp.status_code == 200
        assert "anmelden" in resp.get_data(as_text=True).lower()

    def test_wein_bearbeiten_nicht_gefunden(self, client):
        self._login_als_user(client)
        resp = client.post(
            "/wines/9999/edit",
            data={"name": "X"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Wein nicht gefunden" in resp.get_data(as_text=True)

    def test_wein_bearbeiten_leerer_name(self, client, db):
        from app.models.wein import Wein

        self._login_als_user(client)
        wein = Wein.query.first()
        wein_id = wein.id
        original_name = wein.name
        resp = client.post(
            f"/wines/{wein_id}/edit",
            data={
                "name": "",
                "liter": "5",
                "ingredients": "A, B",
                "description": "Text",
                "brewing_instructions": "Anleitung",
                "brewing_time": "10",
                "alcohol_content": "11",
            },
        )
        assert resp.status_code == 200
        db.session.refresh(wein)
        assert wein.name == original_name

    def test_wein_bearbeiten_parse_fallbacks(self, client, db):
        from app.models.wein import Wein

        self._login_als_user(client)
        wein = Wein.query.first()
        original_liter = wein.liter
        original_brauzeit = wein.brauzeit
        resp = client.post(
            f"/wines/{wein.id}/edit",
            data={
                "name": "Fallback Wein",
                "liter": "kein_float",
                "ingredients": "Trauben, Zucker",
                "description": "Neu",
                "brewing_instructions": "Neu",
                "brewing_time": "kein_int",
                "alcohol_content": "10,5",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        db.session.refresh(wein)
        assert wein.name == "Fallback Wein"
        assert wein.liter == original_liter
        assert wein.brauzeit == original_brauzeit
        assert wein.alkoholgehalt == 10.5

    def test_wein_loeschen_nicht_gefunden_als_admin(self, client):
        self._login_als_admin(client)
        resp = client.post("/wines/9999/delete", follow_redirects=True)
        assert resp.status_code == 200
        assert "Wein nicht gefunden" in resp.get_data(as_text=True)


class TestWeinAPI:
    def test_api_wein_liste(self, client, admin_token):
        resp = client.get("/api/v1/wines/", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_api_wein_ohne_token(self, client):
        resp = client.get("/api/v1/wines/")
        assert resp.status_code == 401

    def test_api_wein_anlegen(self, client, user_token):
        resp = client.post(
            "/api/v1/wines/",
            json={
                "name": "API Wein",
                "liter": 5.0,
                "zutaten": ["1kg Trauben"],
                "brauzeit": 6,
                "alkoholgehalt": 11.5,
            },
            headers=auth_header(user_token),
        )
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "API Wein"

    def test_api_wein_detail(self, client, admin_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.get(f"/api/v1/wines/{wein_id}", headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_api_wein_detail_nicht_gefunden(self, client, admin_token):
        resp = client.get("/api/v1/wines/9999", headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_api_wein_aktualisieren_put(self, client, user_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.put(
            f"/api/v1/wines/{wein_id}",
            json={
                "name": "API Update Wein",
                "liter": 7.0,
                "zutaten": ["2kg Trauben"],
                "beschreibung": "Aktualisiert",
                "brauanweisung": "Mischen",
                "brauzeit": 7,
                "alkoholgehalt": 12.0,
            },
            headers=auth_header(user_token),
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "API Update Wein"

    def test_api_wein_patch(self, client, user_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.patch(
            f"/api/v1/wines/{wein_id}",
            json={"name": "Patch Wein"},
            headers=auth_header(user_token),
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Patch Wein"

    def test_api_wein_put_nicht_gefunden(self, client, user_token):
        resp = client.put(
            "/api/v1/wines/9999",
            json={
                "name": "X",
                "liter": 1.0,
                "zutaten": ["A"],
                "beschreibung": "B",
                "brauanweisung": "C",
                "brauzeit": 1,
                "alkoholgehalt": 1.0,
            },
            headers=auth_header(user_token),
        )
        assert resp.status_code == 404

    def test_api_wein_patch_nicht_gefunden(self, client, user_token):
        resp = client.patch(
            "/api/v1/wines/9999",
            json={"name": "X"},
            headers=auth_header(user_token),
        )
        assert resp.status_code == 404

    def test_api_wein_loeschen_kein_admin(self, client, user_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.delete(
            f"/api/v1/wines/{wein_id}", headers=auth_header(user_token)
        )
        assert resp.status_code == 403

    def test_api_wein_loeschen_als_admin(self, client, admin_token, db):
        from app.models.wein import Wein

        wein_id = Wein.query.first().id
        resp = client.delete(
            f"/api/v1/wines/{wein_id}", headers=auth_header(admin_token)
        )
        assert resp.status_code == 204

    def test_api_wein_loeschen_nicht_gefunden_als_admin(self, client, admin_token):
        resp = client.delete("/api/v1/wines/9999", headers=auth_header(admin_token))
        assert resp.status_code == 404
