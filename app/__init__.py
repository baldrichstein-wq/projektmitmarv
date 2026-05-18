import os

from flask import Flask

from config import config
from .extensions import db, jwt, api


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Extensions initialisieren
    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    # Blueprints registrieren (werden in späteren Commits hinzugefügt)
    _register_blueprints(app)

    with app.app_context():
        db.create_all()
        _seed_datenbank()

    return app


def _register_blueprints(app: Flask) -> None:
    # Blueprints werden schrittweise in Commit 3 & 4 registriert
    pass


def _seed_datenbank() -> None:
    # Seed-Daten werden in Commit 2 nach Erstellung der Modelle hinzugefügt
    pass
