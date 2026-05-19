import os

from flask import Flask, flash, jsonify, redirect, request, url_for
from flask_jwt_extended import get_jwt, unset_jwt_cookies

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
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "Bearer Auth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "bearerFormat": "JWT",
                    "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token",
                }
            }
        },
    }
    api.init_app(app)

    def _jwt_fail_response(message: str, status_code: int = 401):
        if request.path.startswith("/api/"):
            return jsonify(msg=message), status_code

        flash(
            "Sitzung abgelaufen oder ungueltig. Bitte melde dich erneut an.", "warning"
        )
        response = redirect(url_for("auth.anmeldung"))
        unset_jwt_cookies(response)
        return response

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return _jwt_fail_response("Token has expired")

    @jwt.invalid_token_loader
    def invalid_token_callback(reason: str):
        return _jwt_fail_response(reason, status_code=422)

    @app.context_processor
    def inject_jwt_context() -> dict[str, str]:
        role = "gast"
        name = "Gast"

        try:
            claims = get_jwt()
            role = claims.get("rolle", role)
            name = claims.get("name", name)
        except Exception:
            pass

        return {"role": role, "name": name}

    # Blueprints registrieren (werden in späteren Commits hinzugefügt)
    _register_blueprints(app)

    with app.app_context():
        # Modelle importieren damit db.create_all() alle Tabellen kennt
        from .models import Benutzer, Essen, Wein  # noqa: F401

        db.create_all()
        _seed_datenbank()

    return app


def _register_blueprints(app: Flask) -> None:
    from .blueprints.main.routes import bp as main_bp
    from .blueprints.auth.routes import bp as auth_bp
    from .blueprints.essen.routes import bp as essen_bp
    from .blueprints.wein.routes import bp as wein_bp
    from .blueprints.benutzer.routes import bp as benutzer_bp
    from .blueprints.api.auth import bp as api_auth_bp
    from .blueprints.api.essen import bp as api_essen_bp
    from .blueprints.api.wein import bp as api_wein_bp
    from .blueprints.api.benutzer import bp as api_benutzer_bp

    # HTML-Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(essen_bp)
    app.register_blueprint(wein_bp)
    app.register_blueprint(benutzer_bp)

    # API-Blueprints (flask-smorest registriert Swagger automatisch)
    api.register_blueprint(api_auth_bp)
    api.register_blueprint(api_essen_bp)
    api.register_blueprint(api_wein_bp)
    api.register_blueprint(api_benutzer_bp)


def _seed_datenbank() -> None:
    from .models.benutzer import Benutzer
    from .models.essen import Essen
    from .models.wein import Wein

    # Nur seeden wenn die DB leer ist
    if Benutzer.query.count() == 0:
        admin = Benutzer(name="Admin", email="admin@rezepte.de", rolle="admin")
        admin.set_password("admin123")
        benutzer = Benutzer(
            name="Benutzer", email="benutzer@rezepte.de", rolle="benutzer"
        )
        benutzer.set_password("benutzer123")
        db.session.add_all([admin, benutzer])

    if Essen.query.count() == 0:
        beispiel_essen = Essen(
            name="Kaiserliches Kräuter-Kaninchen mit Rosmarin",
            personenanzahl=4,
            zutaten=[
                "0,5 kg Kaninchen",
                "4 Zweige frischer Rosmarin",
                "2 Zweige Thymian",
                "1 Zehe Knoblauch (zerdrückt)",
                "Salz & Pfeffer",
                "etwas Butter oder Olivenöl",
                "Bräter",
            ],
            beschreibung=(
                "Ein köstliches Gericht, das die Aromen von frischen Kräutern und zartem "
                "Kaninchen vereint. Perfekt für ein festliches Mahl oder einen besonderen Anlass."
            ),
            kochanweisung=(
                "Das Fleisch mit Salz, Pfeffer und dem zerdrückten Knoblauch kräftig einmassieren. "
                "Die Kräuter fein hacken und unter die Gewürzmischung rühren. Das Kaninchen damit "
                "bestreichen und mindestens 2 Stunden ziehen lassen. Bei mittlerer Hitze im Ofen "
                "goldbraun braten, bis es nach Sieg riecht!"
            ),
            kochzeit=120,
        )
        db.session.add(beispiel_essen)

    if Wein.query.count() == 0:
        beispiel_wein = Wein(
            name="Holunder Johannisbeer Wein",
            liter=5.0,
            zutaten=[
                "1 Pack Weinhefe Sorte Portwein",
                "500g Johannisbeeren Schwarz",
                "1000g Holunderbeeren",
                "1800g Zucker",
                "Wasser bis 5l Ansatz erreicht",
                "Starsan für Desinfektion von Brauutensilien",
                "5g Hefenährsalz",
                "Gärbehälter mit Gärstopfen",
                "Dampfentsafter",
            ],
            beschreibung=(
                "Ein sehr kräftiger Wein mit eigenwilligem Geschmack, bei dem Holunder und "
                "Johannisbeere zusammenwirken."
            ),
            brauanweisung=(
                "Alle Utensilien sauber vorbereiten, Früchte entsaften, Zucker und Hefe "
                "einrühren und in einem sauberen Gärbehälter gären lassen."
            ),
            brauzeit=8,
            alkoholgehalt=15.0,
        )
        db.session.add(beispiel_wein)

    db.session.commit()
