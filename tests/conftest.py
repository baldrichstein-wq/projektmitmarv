import pytest

from app import create_app
from app.extensions import db as _db
from app.models.benutzer import Benutzer
from app.models.essen import Essen
from app.models.wein import Wein


@pytest.fixture(scope="session")
def app():
    flask_app = create_app("testing")
    return flask_app


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.drop_all()  # frischer Zustand für jeden Test
        _db.create_all()
        _seed_testdaten()
        yield _db
        _db.session.remove()
        _db.drop_all()


def _seed_testdaten():
    if Benutzer.query.count() == 0:
        admin = Benutzer(name="Admin", email="admin@test.de", rolle="admin")
        admin.set_password("admin123")
        benutzer = Benutzer(name="Benutzer", email="benutzer@test.de", rolle="benutzer")
        benutzer.set_password("benutzer123")
        _db.session.add_all([admin, benutzer])

    if Essen.query.count() == 0:
        essen = Essen(
            name="Test-Essen",
            personenanzahl=2,
            zutaten=["200g Nudeln", "1 Dose Tomaten"],
            beschreibung="Ein einfaches Testgericht",
            kochanweisung="Nudeln kochen, Soße erhitzen.",
            kochzeit=20,
        )
        _db.session.add(essen)

    if Wein.query.count() == 0:
        wein = Wein(
            name="Test-Wein",
            liter=5.0,
            zutaten=["1kg Trauben", "500g Zucker"],
            beschreibung="Ein einfacher Testwein",
            brauanweisung="Alles mischen und gären lassen.",
            brauzeit=4,
            alkoholgehalt=12.0,
        )
        _db.session.add(wein)

    _db.session.commit()


@pytest.fixture(scope="function")
def client(app, db):
    return app.test_client()


def login_als(client, email: str, password: str):
    """Meldet einen Benutzer über die WebUI an und setzt den JWT-Cookie."""
    resp = client.post(
        "/anmeldung",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
    return resp


@pytest.fixture(scope="function")
def admin_token(client):
    resp = client.post("/api/v1/auth/login", json={"email": "admin@test.de", "password": "admin123"})
    return resp.get_json()["access_token"]


@pytest.fixture(scope="function")
def benutzer_token(client):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "benutzer@test.de", "password": "benutzer123"}
    )
    return resp.get_json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
