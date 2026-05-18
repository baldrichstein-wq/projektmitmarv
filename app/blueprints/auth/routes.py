from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from app.extensions import db
from app.models.benutzer import Benutzer

bp = Blueprint("auth", __name__)


def _aktuelle_rolle() -> str:
    """Gibt die Rolle aus dem JWT-Cookie zurück (oder 'gast' wenn nicht angemeldet)."""
    try:
        # get_jwt() wirft, wenn kein gültiger Token vorhanden ist
        return get_jwt().get("rolle", "gast")
    except Exception:
        return "gast"


@bp.route("/anmeldung", methods=["GET", "POST"])
@jwt_required(optional=True)
def anmeldung():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = Benutzer.query.filter_by(email=email).first()
        if user and user.check_password(password):
            additional_claims = {"rolle": user.rolle, "name": user.name}
            access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
            resp = redirect(url_for("main.home"))
            set_access_cookies(resp, access_token)
            flash(f"Willkommen {user.name}!", "success")
            return resp
        flash("Ungültige Anmeldedaten.", "danger")

    return render_template("auth/anmeldung.html", role=_aktuelle_rolle())


@bp.route("/registrierung", methods=["GET", "POST"])
@jwt_required(optional=True)
def registrierung():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("Bitte alle Felder ausfüllen.", "danger")
            return redirect(url_for("auth.registrierung"))

        if Benutzer.query.filter_by(email=email).first():
            flash("Diese E-Mail-Adresse ist bereits registriert.", "danger")
            return redirect(url_for("auth.registrierung"))

        neuer_benutzer = Benutzer(name=name, email=email, rolle="benutzer")
        neuer_benutzer.set_password(password)
        db.session.add(neuer_benutzer)
        db.session.commit()

        flash("Registrierung erfolgreich! Du kannst dich jetzt anmelden.", "success")
        return redirect(url_for("auth.anmeldung"))

    return render_template("auth/registrierung.html", role=_aktuelle_rolle())


@bp.route("/abmeldung")
@jwt_required(optional=True)
def abmeldung():
    resp = redirect(url_for("main.home"))
    unset_jwt_cookies(resp)
    flash("Erfolgreich abgemeldet.", "success")
    return resp
