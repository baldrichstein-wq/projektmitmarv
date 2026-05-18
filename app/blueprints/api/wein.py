from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.models.wein import Wein
from app.schemas.wein import WeinSchema

bp = Blueprint("api_wein", __name__, url_prefix="/api/v1/wein", description="Wein-Rezepte")


@bp.route("/")
class WeinListe(MethodView):
    @jwt_required()
    @bp.response(200, WeinSchema(many=True))
    def get(self):
        """Alle Wein-Rezepte abrufen"""
        return Wein.query.all()

    @jwt_required()
    @bp.arguments(WeinSchema)
    @bp.response(201, WeinSchema)
    def post(self, daten):
        """Neues Wein-Rezept anlegen"""
        claims = get_jwt()
        if claims.get("rolle") not in ("benutzer", "admin"):
            abort(403, message="Keine Berechtigung.")
        neuer_wein = Wein(**daten)
        db.session.add(neuer_wein)
        db.session.commit()
        return neuer_wein


@bp.route("/<int:wein_id>")
class WeinDetail(MethodView):
    @jwt_required()
    @bp.response(200, WeinSchema)
    def get(self, wein_id):
        """Einzelnes Wein-Rezept abrufen"""
        return Wein.query.get_or_404(wein_id)

    @jwt_required()
    @bp.arguments(WeinSchema)
    @bp.response(200, WeinSchema)
    def put(self, daten, wein_id):
        """Wein-Rezept aktualisieren"""
        claims = get_jwt()
        if claims.get("rolle") not in ("benutzer", "admin"):
            abort(403, message="Keine Berechtigung.")
        wein = Wein.query.get_or_404(wein_id)
        for key, value in daten.items():
            setattr(wein, key, value)
        db.session.commit()
        return wein

    @jwt_required()
    @bp.response(204)
    def delete(self, wein_id):
        """Wein-Rezept löschen (nur Admin)"""
        claims = get_jwt()
        if claims.get("rolle") != "admin":
            abort(403, message="Nur Administratoren können Wein-Rezepte löschen.")
        wein = Wein.query.get_or_404(wein_id)
        db.session.delete(wein)
        db.session.commit()
