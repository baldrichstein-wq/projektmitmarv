from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.benutzer import Benutzer

bp = Blueprint("benutzer", __name__)

ERLAUBTE_ROLLEN = {"gast", "benutzer", "admin"}


@bp.route("/benutzer", methods=["GET", "POST"])
def verwalte_benutzer():
    role = session.get("user_role", "gast")
    if role != "admin":
        flash("Zugriff verweigert: Nur Administratoren dürfen Benutzer verwalten.", "danger")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if Benutzer.query.filter_by(email=email).first():
            flash("Diese E-Mail-Adresse ist bereits vergeben.", "danger")
        else:
            neuer = Benutzer(name=name, email=email, rolle="benutzer")
            neuer.set_password(password)
            db.session.add(neuer)
            db.session.commit()
            flash(f'Benutzer "{name}" wurde angelegt.', "success")

        return redirect(url_for("benutzer.verwalte_benutzer"))

    alle_benutzer = Benutzer.query.all()
    return render_template("benutzer/benutzer.html", users=alle_benutzer, role=role)


@bp.route("/benutzer/rolle_aendern/<int:user_id>", methods=["POST"])
def rolle_update(user_id):
    if session.get("user_role") != "admin":
        flash("Nicht autorisiert.", "danger")
        return redirect(url_for("main.home"))

    neue_rolle = request.form.get("rolle", "").strip()
    if neue_rolle not in ERLAUBTE_ROLLEN:
        flash("Ungültige Rolle.", "danger")
        return redirect(url_for("benutzer.verwalte_benutzer"))

    benutzer = Benutzer.query.get_or_404(user_id)
    benutzer.rolle = neue_rolle
    db.session.commit()
    flash(f"Rolle für {benutzer.name} wurde auf {neue_rolle} aktualisiert.", "success")
    return redirect(url_for("benutzer.verwalte_benutzer"))
