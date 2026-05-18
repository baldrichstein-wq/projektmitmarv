

class TestAnmeldung:
    def test_anmeldung_gueltig(self, client):
        resp = client.post(
            "/anmeldung",
            data={"email": "admin@test.de", "password": "admin123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_anmeldung_ungueltig(self, client):
        resp = client.post(
            "/anmeldung",
            data={"email": "admin@test.de", "password": "falsch"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Ungültige Anmeldedaten" in resp.get_data(as_text=True)

    def test_anmeldung_unbekannte_email(self, client):
        resp = client.post(
            "/anmeldung",
            data={"email": "unbekannt@test.de", "password": "irgendwas"},
            follow_redirects=True,
        )
        assert "Ungültige Anmeldedaten" in resp.get_data(as_text=True)


class TestRegistrierung:
    def test_registrierung_gueltig(self, client):
        resp = client.post(
            "/registrierung",
            data={"name": "Neu", "email": "neu@test.de", "password": "test123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Registrierung erfolgreich" in resp.get_data(as_text=True)

    def test_registrierung_doppelte_email(self, client):
        resp = client.post(
            "/registrierung",
            data={"name": "Doppelt", "email": "admin@test.de", "password": "test123"},
            follow_redirects=True,
        )
        assert "bereits registriert" in resp.get_data(as_text=True)

    def test_registrierung_leere_felder(self, client):
        resp = client.post(
            "/registrierung",
            data={"name": "", "email": "", "password": ""},
            follow_redirects=True,
        )
        assert "Bitte alle Felder ausfüllen" in resp.get_data(as_text=True)


class TestAbmeldung:
    def test_abmeldung_redirect(self, client):
        client.post("/anmeldung", data={"email": "admin@test.de", "password": "admin123"})
        resp = client.get("/abmeldung", follow_redirects=True)
        assert resp.status_code == 200
        assert "Erfolgreich abgemeldet" in resp.get_data(as_text=True)


class TestRollenzugriff:
    def test_benutzer_verwaltung_nur_admin(self, client):
        resp = client.get("/benutzer", follow_redirects=True)
        assert "Zugriff verweigert" in resp.get_data(as_text=True)
