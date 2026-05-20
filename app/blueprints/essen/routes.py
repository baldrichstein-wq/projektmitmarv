import json

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.essen import Essen
from app.utils import jwt_rolle

bp = Blueprint("essen", __name__)


def _parse_int(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


@bp.route("/foods", methods=["GET", "POST"])
@jwt_required(optional=True)
def verwalte_essen():
    role = jwt_rolle()
    if role == "gast":
        flash("Bitte melden Sie sich an.", "danger")
        return redirect(url_for("auth.anmeldung"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        personen = int(request.form.get("personenanzahl", 4) or 4)
        zutaten = [
            z.strip()
            for z in request.form.get("ingredients", "").split(",")
            if z.strip()
        ]
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


@bp.route("/foods/<int:essen_id>/edit", methods=["GET", "POST"])
@jwt_required(optional=True)
def bearbeite_essen(essen_id):
    role = jwt_rolle()
    if role == "gast":
        flash("Bitte melde dich an.", "danger")
        return redirect(url_for("auth.anmeldung"))

    aktuelles_essen = db.session.get(Essen, essen_id)
    if not aktuelles_essen:
        flash("Rezept nicht gefunden.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    if request.method == "POST":
        aktuelles_essen.name = request.form.get("name", "").strip()
        aktuelles_essen.personenanzahl = int(request.form.get("personenanzahl") or 1)
        aktuelles_essen.zutaten = [
            z.strip()
            for z in request.form.get("ingredients", "").split(",")
            if z.strip()
        ]
        aktuelles_essen.beschreibung = request.form.get("description", "").strip()
        aktuelles_essen.kochanweisung = request.form.get("kochanweisung", "").strip()
        aktuelles_essen.kochzeit = int(request.form.get("kochzeit") or 0)
        db.session.commit()
        flash(f'Rezept "{aktuelles_essen.name}" wurde aktualisiert.', "success")
        return redirect(url_for("essen.verwalte_essen"))

    return render_template("essen/essen_edit.html", essen=aktuelles_essen, role=role)


@bp.route("/foods/<int:essen_id>/delete", methods=["POST"])
@jwt_required(optional=True)
def loesche_essen(essen_id):
    if jwt_rolle() != "admin":
        flash("Nur Administratoren können Rezepte löschen.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    essen = db.session.get(Essen, essen_id)
    if not essen:
        flash("Rezept nicht gefunden.", "danger")
        return redirect(url_for("essen.verwalte_essen"))
    db.session.delete(essen)
    db.session.commit()
    flash("Rezept wurde erfolgreich gelöscht.", "success")
    return redirect(url_for("essen.verwalte_essen"))


@bp.route("/foods/export", methods=["GET"])
@jwt_required(optional=True)
def exportiere_essen_json():
    if jwt_rolle() != "admin":
        flash("Nur Administratoren dürfen Rezepte exportieren.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    daten = [
        {
            "name": eintrag.name,
            "personenanzahl": eintrag.personenanzahl,
            "zutaten": eintrag.zutaten or [],
            "beschreibung": eintrag.beschreibung,
            "kochanweisung": eintrag.kochanweisung,
            "kochzeit": eintrag.kochzeit,
        }
        for eintrag in Essen.query.order_by(Essen.id.asc()).all()
    ]

    return Response(
        json.dumps(daten, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=essen_export.json"},
    )


@bp.route("/foods/import", methods=["POST"])
@jwt_required(optional=True)
def importiere_essen_json():
    if jwt_rolle() != "admin":
        flash("Nur Administratoren dürfen Rezepte importieren.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    datei = request.files.get("json_file")
    if not datei or not datei.filename:
        flash("Bitte wählen Sie eine JSON-Datei aus.", "warning")
        return redirect(url_for("essen.verwalte_essen"))

    try:
        roh_daten = json.load(datei.stream)
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash("Ungültiges JSON-Format.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    if isinstance(roh_daten, dict):
        eintraege = roh_daten.get("items", [])
    else:
        eintraege = roh_daten

    if not isinstance(eintraege, list):
        flash("JSON muss eine Liste von Rezepten enthalten.", "danger")
        return redirect(url_for("essen.verwalte_essen"))

    clear_table = request.form.get("clear_table") == "on"
    if clear_table:
        db.session.query(Essen).delete()
        db.session.commit()
        flash("Bestehende Rezepte wurden gelöscht.", "info")

    importiert = 0
    uebersprungen = 0

    for eintrag in eintraege:
        if not isinstance(eintrag, dict):
            uebersprungen += 1
            continue

        name = str(eintrag.get("name", "")).strip()
        if not name:
            uebersprungen += 1
            continue

        zutaten = eintrag.get("zutaten", [])
        if isinstance(zutaten, str):
            zutaten = [z.strip() for z in zutaten.split(",") if z.strip()]
        elif isinstance(zutaten, list):
            zutaten = [str(z).strip() for z in zutaten if str(z).strip()]
        else:
            zutaten = []

        rezept = Essen(
            name=name,
            personenanzahl=_parse_int(eintrag.get("personenanzahl", 2), 2),
            zutaten=zutaten,
            beschreibung=str(eintrag.get("beschreibung", "") or "").strip(),
            kochanweisung=str(eintrag.get("kochanweisung", "") or "").strip(),
            kochzeit=_parse_int(eintrag.get("kochzeit", 0), 0),
        )
        db.session.add(rezept)
        importiert += 1

    if importiert > 0:
        db.session.commit()
        flash(f"{importiert} Rezepte wurden importiert.", "success")
    else:
        flash("Es wurden keine gültigen Rezepte importiert.", "warning")

    if uebersprungen > 0:
        flash(f"{uebersprungen} Einträge wurden übersprungen.", "warning")

    return redirect(url_for("essen.verwalte_essen"))
