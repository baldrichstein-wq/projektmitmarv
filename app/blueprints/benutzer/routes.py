from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.benutzer import Benutzer
from app.utils import jwt_rolle

bp = Blueprint("benutzer", __name__)

ERLAUBTE_ROLLEN = {"gast", "user", "admin"}


@bp.route("/users", methods=["GET", "POST"])
@jwt_required(optional=True)
def verwalte_benutzer():
    role = jwt_rolle()
    if role != "admin":
        flash(
            "Zugriff verweigert: Nur Administratoren dürfen Benutzer verwalten.",
            "danger",
        )
        return redirect(url_for("main.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if Benutzer.query.filter_by(email=email).first():
            flash("Diese E-Mail-Adresse ist bereits vergeben.", "danger")
        else:
            neuer = Benutzer(name=name, email=email, rolle="user")
            neuer.set_password(password)
            db.session.add(neuer)
            db.session.commit()
            flash(f'Benutzer "{name}" wurde angelegt.', "success")

        return redirect(url_for("benutzer.verwalte_benutzer"))

    alle_benutzer = Benutzer.query.all()
    current_user_email = get_jwt_identity()
    return render_template(
        "benutzer/benutzer.html",
        users=alle_benutzer,
        role=role,
        current_user_email=current_user_email,
    )


@bp.route("/users/<int:user_id>/role", methods=["POST"])
@jwt_required(optional=True)
def rolle_update(user_id):
    if jwt_rolle() != "admin":
        flash("Nicht autorisiert.", "danger")
        return redirect(url_for("main.home"))

    neue_rolle = request.form.get("rolle", "").strip()
    if neue_rolle not in ERLAUBTE_ROLLEN:
        flash("Ungültige Rolle.", "danger")
        return redirect(url_for("benutzer.verwalte_benutzer"))

    benutzer = db.session.get(Benutzer, user_id)
    if not benutzer:
        flash("Benutzer nicht gefunden.", "danger")
        return redirect(url_for("benutzer.verwalte_benutzer"))

    benutzer.rolle = neue_rolle
    db.session.commit()
    flash(f"Rolle für {benutzer.name} wurde auf {neue_rolle} aktualisiert.", "success")
    return redirect(url_for("benutzer.verwalte_benutzer"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@jwt_required(optional=True)
def benutzer_loeschen(user_id):
    if jwt_rolle() != "admin":
        flash("Nicht autorisiert.", "danger")
        return redirect(url_for("main.home"))

    current_user_email = get_jwt_identity()

    benutzer = db.session.get(Benutzer, user_id)
    if not benutzer:
        flash("Benutzer nicht gefunden.", "danger")
        return redirect(url_for("benutzer.verwalte_benutzer"))

    if current_user_email is not None and benutzer.email == current_user_email:
        flash("Du kannst dein eigenes Benutzerkonto nicht löschen.", "danger")
        return redirect(url_for("benutzer.verwalte_benutzer"))

    db.session.delete(benutzer)
    db.session.commit()
    flash(f'Benutzer "{benutzer.name}" wurde gelöscht.', "success")
    return redirect(url_for("benutzer.verwalte_benutzer"))
