from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.essen import Essen
from app.utils import jwt_rolle

bp = Blueprint("essen", __name__)


@bp.route("/essen", methods=["GET", "POST"])
@jwt_required(optional=True)
def verwalte_essen():
    role = jwt_rolle()
    if role == "gast":
        flash("Bitte melden Sie sich an.", "danger")
        return redirect(url_for("auth.anmeldung"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        personen = int(request.form.get("personenanzahl", 4) or 4)
        zutaten = [z.strip() for z in request.form.get("ingredients", "").split(",") if z.strip()]
        beschreibung = request.form.get("description", "").strip()
        kochanweisung = request.form.get("kochanweisung", "").strip()
        kochzeit = int(request.form.get("kochzeit", 0) or 0)

        neues_essen = Essen(
            name=name,
            personenanzahl=personen,
            zutaten=zutaten,
            beschreibung=beschreibung,
            kochanweisung=kochanweisung,
            kochzeit=kochzeit,
        )
        db.session.add(neues_essen)
        db.session.commit()
        flash("Essen gespeichert.", "success")
        return redirect(url_for("essen.verwalte_essen"))

    speisen_liste = Essen.query.all()
    return render_template("essen/essen.html", essen=speisen_liste, role=role)


@bp.route("/essen/bearbeiten/<int:essen_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def bearbeite_essen(essen_id):
    role = jwt_rolle()
    if role == "gast":
        flash("Bitte melde dich an.", "danger")
        return redirect(url_for("auth.anmeldung"))

    aktuelles_essen = Essen.query.get_or_404(essen_id)

    if request.method == "POST":
        aktuelles_essen.name = request.form.get("name", "").strip()
        aktuelles_essen.personenanzahl = int(request.form.get("personenanzahl") or 1)
        aktuelles_essen.zutaten = [
            z.strip() for z in request.form.get("ingredients", "").split(",") if z.strip()
        ]
        aktuelles_essen.beschreibung = request.form.get("description", "").strip()
        aktuelles_essen.kochanweisung = request.form.get("kochanweisung", "").strip()
        aktuelles_essen.kochzeit = int(request.form.get("kochzeit") or 0)
        db.session.commit()
        flash(f'Rezept "{aktuelles_essen.name}" wurde aktualisiert.', "success")
        return redirect(url_for("essen.verwalte_essen"))

    return render_template("essen/essen_edit.html", essen=aktuelles_essen, role=role)


@bp.route("/essen/loeschen/<int:essen_id>", methods=["POST"])
@jwt_required(optional=True)
def loesche_essen(essen_id):
    if jwt_rolle() != "admin":
        flash("Nur Administratoren können Rezepte löschen.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    essen = Essen.query.get_or_404(essen_id)
    db.session.delete(essen)
    db.session.commit()
    flash("Rezept wurde erfolgreich gelöscht.", "success")
    return redirect(url_for("essen.verwalte_essen"))
