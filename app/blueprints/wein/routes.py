from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.wein import Wein
from app.utils import jwt_rolle

bp = Blueprint("wein", __name__)


@bp.route("/wines", methods=["GET", "POST"])
@jwt_required(optional=True)
def wein_verwalten():
    role = jwt_rolle()
    if role not in ("user", "admin"):
        flash("Bitte melde dich an, um Weine zu sehen.", "danger")
        return redirect(url_for("auth.anmeldung"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        liter = float(request.form.get("liter", 5) or 5)
        zutaten = [
            z.strip()
            for z in request.form.get("ingredients", "").split(",")
            if z.strip()
        ]
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


@bp.route("/wines/<int:wine_id>/edit", methods=["GET", "POST"])
@jwt_required(optional=True)
def update_wine(wine_id):
    role = jwt_rolle()
    if role not in ("user", "admin"):
        flash("Nur Administratoren und Benutzer können Weine bearbeiten.", "danger")
        return redirect(url_for("wein.wein_verwalten"))

    wein = db.session.get(Wein, wine_id)
    if not wein:
        flash("Wein nicht gefunden.", "danger")
        return redirect(url_for("wein.wein_verwalten"))

    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", "").strip(),
            "liter": request.form.get("liter", str(wein.liter)),
            "ingredients": request.form.get("ingredients", ""),
            "description": request.form.get("description", "").strip(),
            "brewing_instructions": request.form.get(
                "brewing_instructions", ""
            ).strip(),
            "brewing_time": request.form.get("brewing_time", str(wein.brauzeit)),
            "alcohol_content": request.form.get(
                "alcohol_content", str(wein.alkoholgehalt)
            ),
        }

        name = form_data["name"]
        if not name:
            return render_template(
                "wein/wein_edit.html",
                wine=wein,
                role=role,
                form_error="Der Name des Weins darf nicht leer sein.",
                form_data=form_data,
            )

        def _parse_float(value: str, fallback: float) -> float:
            try:
                return float(str(value).replace(",", "."))
            except (TypeError, ValueError):
                return fallback

        def _parse_int(value: str, fallback: int) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return fallback

        wein.name = name
        wein.liter = _parse_float(form_data["liter"], wein.liter)
        wein.zutaten = [
            z.strip() for z in form_data["ingredients"].split(",") if z.strip()
        ]
        wein.beschreibung = form_data["description"]
        wein.brauanweisung = form_data["brewing_instructions"]
        wein.brauzeit = _parse_int(form_data["brewing_time"], wein.brauzeit)
        wein.alkoholgehalt = _parse_float(
            form_data["alcohol_content"], wein.alkoholgehalt
        )
        db.session.commit()
        flash(f'Wein "{wein.name}" wurde aktualisiert!', "success")
        return redirect(url_for("wein.wein_verwalten"))

    return render_template(
        "wein/wein_edit.html", wine=wein, role=role, form_error=None, form_data=None
    )


@bp.route("/wines/<int:wine_id>/delete", methods=["POST"])
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
