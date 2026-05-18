from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.benutzer import Benutzer

bp = Blueprint("auth", __name__)


@bp.route("/anmeldung", methods=["GET", "POST"])
def anmeldung():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = Benutzer.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_email"] = user.email
            session["user_name"] = user.name
            session["user_role"] = user.rolle
            flash(f"Willkommen {user.name}!", "success")
            return redirect(url_for("main.home"))
        flash("Ungültige Anmeldedaten.", "danger")

    return render_template("auth/anmeldung.html", role=session.get("user_role", "gast"))


@bp.route("/registrierung", methods=["GET", "POST"])
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

    return render_template("auth/registrierung.html", role=session.get("user_role", "gast"))


@bp.route("/abmeldung")
def abmeldung():
    session.clear()
    flash("Erfolgreich abgemeldet.", "success")
    return redirect(url_for("main.home"))
