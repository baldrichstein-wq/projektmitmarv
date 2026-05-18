from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.wein import Wein
from app.utils import jwt_rolle

bp = Blueprint("wein", __name__)


@bp.route("/wein", methods=["GET", "POST"])
@jwt_required(optional=True)
def wein_verwalten():
    role = jwt_rolle()
    if role not in ("benutzer", "admin"):
        flash("Bitte melde dich an, um Weine zu sehen.", "danger")
        return redirect(url_for("auth.anmeldung"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        liter = float(request.form.get("liter", 5) or 5)
        zutaten = [z.strip() for z in request.form.get("ingredients", "").split(",") if z.strip()]
        beschreibung = request.form.get("description", "").strip()
        brauanweisung = request.form.get("brewing_instructions", "").strip()
        brauzeit = int(request.form.get("brewing_time", 0) or 0)
        alkoholgehalt = float(request.form.get("alcohol_content", 0) or 0)

        neuer_wein = Wein(
            name=name,
            liter=liter,
            zutaten=zutaten,
            beschreibung=beschreibung,
            brauanweisung=brauanweisung,
            brauzeit=brauzeit,
            alkoholgehalt=alkoholgehalt,
        )
        db.session.add(neuer_wein)
        db.session.commit()
        flash(f'Wein "{name}" hinzugefügt!', "success")
        return redirect(url_for("wein.wein_verwalten"))

    weine = Wein.query.all()
    return render_template("wein/wein.html", wines=weine, role=role)


@bp.route("/wein_edit/<int:wine_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def update_wine(wine_id):
    role = jwt_rolle()
    if role not in ("benutzer", "admin"):
        flash("Nur Administratoren und Benutzer können Weine bearbeiten.", "danger")
        return redirect(url_for("wein.wein_verwalten"))

    wein = db.session.get(Wein, wine_id)
    if not wein:
        flash("Wein nicht gefunden.", "danger")
        return redirect(url_for("wein.wein_verwalten"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Fehler: Der Name des Weins darf nicht leer sein!", "danger")
            return redirect(url_for("wein.update_wine", wine_id=wine_id))

        wein.name = name
        wein.liter = float(request.form.get("liter", wein.liter) or wein.liter)
        wein.zutaten = [z.strip() for z in request.form.get("ingredients", "").split(",") if z.strip()]
        wein.beschreibung = request.form.get("description", "").strip()
        wein.brauanweisung = request.form.get("brewing_instructions", "").strip()
        wein.brauzeit = int(request.form.get("brewing_time", 0) or 0)
        wein.alkoholgehalt = float(request.form.get("alcohol_content", 0) or 0)
        db.session.commit()
        flash(f'Wein "{wein.name}" wurde aktualisiert!', "success")
        return redirect(url_for("wein.wein_verwalten"))

    return render_template("wein/wein_edit.html", wine=wein, role=role)


@bp.route("/wein/loeschen/<int:wine_id>", methods=["POST"])
@jwt_required(optional=True)
def loesche_wein(wine_id):
    if jwt_rolle() != "admin":
        flash("Nur Administratoren können Weine löschen.", "danger")
        return redirect(url_for("wein.wein_verwalten"))

    wein = db.session.get(Wein, wine_id)
    if not wein:
        flash("Wein nicht gefunden.", "danger")
        return redirect(url_for("wein.wein_verwalten"))
    db.session.delete(wein)
    db.session.commit()
    flash("Wein wurde erfolgreich gelöscht.", "success")
    return redirect(url_for("wein.wein_verwalten"))
