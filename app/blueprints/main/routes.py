
from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required

from app.models.essen import Essen
from app.models.wein import Wein
from app.utils import jwt_name, jwt_rolle

bp = Blueprint("main", __name__)


@bp.route("/")
@jwt_required(optional=True)
def home():
    role = jwt_rolle()
    name = jwt_name()
    return render_template("main/index.html", name=name, role=role)


@bp.route("/ueber-uns")
@jwt_required(optional=True)
def ueber_uns():
    role = jwt_rolle()
    return render_template("main/ueber-uns.html", role=role)


@bp.route("/suche")
@jwt_required(optional=True)
def suche():
    role = jwt_rolle()
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
