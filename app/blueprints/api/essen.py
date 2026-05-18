from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.models.essen import Essen
from app.schemas.essen import EssenSchema

bp = Blueprint("api_essen", __name__, url_prefix="/api/v1/essen", description="Essen-Rezepte")


@bp.route("/")
class EssenListe(MethodView):
    @jwt_required()
    @bp.response(200, EssenSchema(many=True))
    def get(self):
        """Alle Essen-Rezepte abrufen"""
        return Essen.query.all()

    @jwt_required()
    @bp.arguments(EssenSchema)
    @bp.response(201, EssenSchema)
    def post(self, daten):
        """Neues Essen-Rezept anlegen"""
        claims = get_jwt()
        if claims.get("rolle") not in ("benutzer", "admin"):
            abort(403, message="Keine Berechtigung.")
        neues_essen = Essen(**daten)
        db.session.add(neues_essen)
        db.session.commit()
        return neues_essen


@bp.route("/<int:essen_id>")
class EssenDetail(MethodView):
    @jwt_required()
    @bp.response(200, EssenSchema)
    def get(self, essen_id):
        """Einzelnes Essen-Rezept abrufen"""
        essen = db.session.get(Essen, essen_id)
        if not essen:
            abort(404, message="Essen nicht gefunden.")
        return essen

    @jwt_required()
    @bp.arguments(EssenSchema)
    @bp.response(200, EssenSchema)
    def put(self, daten, essen_id):
        """Essen-Rezept aktualisieren"""
        claims = get_jwt()
        if claims.get("rolle") not in ("benutzer", "admin"):
            abort(403, message="Keine Berechtigung.")
        essen = db.session.get(Essen, essen_id)
        if not essen:
            abort(404, message="Essen nicht gefunden.")
        for key, value in daten.items():
            setattr(essen, key, value)
        db.session.commit()
        return essen

    @jwt_required()
    @bp.response(204)
    def delete(self, essen_id):
        """Essen-Rezept löschen (nur Admin)"""
        claims = get_jwt()
        if claims.get("rolle") != "admin":
            abort(403, message="Nur Administratoren können Rezepte löschen.")
        essen = db.session.get(Essen, essen_id)
        if not essen:
            abort(404, message="Essen nicht gefunden.")
        db.session.delete(essen)
        db.session.commit()
