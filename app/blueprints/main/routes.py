import re

from flask import Blueprint, render_template, request, session

from app.models.essen import Essen
from app.models.wein import Wein

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    role = session.get("user_role", "gast")
    name = session.get("user_name", "Gast")
    return render_template("main/index.html", name=name, role=role)


@bp.route("/ueber-uns")
def ueber_uns():
    role = session.get("user_role", "gast")
    return render_template("main/ueber-uns.html", role=role)


@bp.route("/suche")
def suche():
    role = session.get("user_role", "gast")
    query = request.args.get("q", "").strip().lower()

    gefundene_weine = []
    gefundene_speisen = []

    if query:
        for w in Wein.query.all():
            zutaten_string = " ".join(w.zutaten).lower()
            if (
                query in w.name.lower()
                or (w.beschreibung and query in w.beschreibung.lower())
                or query in zutaten_string
            ):
                gefundene_weine.append(w)

        for e in Essen.query.all():
            zutaten_string = " ".join(e.zutaten).lower()
            if (
                query in e.name.lower()
                or (e.beschreibung and query in e.beschreibung.lower())
                or query in zutaten_string
            ):
                gefundene_speisen.append(e)

    return render_template(
        "main/suche.html",
        query=query,
        weine=gefundene_weine,
        speisen=gefundene_speisen,
        role=role,
    )
