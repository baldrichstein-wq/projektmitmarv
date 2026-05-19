from flask.views import MethodView
from flask_jwt_extended import get_jwt
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.blueprints.api.decorators import auth_required
from app.models.wein import Wein
from app.schemas.wein import WeinPatchSchema, WeinSchema

bp = Blueprint(
    "wines", __name__, url_prefix="/api/v1/wines", description="Wine recipes"
)


@bp.route("/")
class WeinListe(MethodView):
    @auth_required(bp)
    @bp.response(200, WeinSchema(many=True))
    def get(self):
        """List all wine recipes"""
        return Wein.query.all()

    @auth_required(bp)
    @bp.arguments(WeinSchema)
    @bp.response(201, WeinSchema)
    def post(self, daten):
        """Create a new wine recipe"""
        claims = get_jwt()
        if claims.get("rolle") not in ("user", "admin"):
            abort(403, message="Insufficient permissions.")
        neuer_wein = Wein(**daten)
        db.session.add(neuer_wein)
        db.session.commit()
        return neuer_wein


@bp.route("/<int:wine_id>")
class WeinDetail(MethodView):
    @auth_required(bp)
    @bp.response(200, WeinSchema)
    def get(self, wine_id):
        """Get a single wine recipe"""
        wein = db.session.get(Wein, wine_id)
        if not wein:
            abort(404, message="Wine recipe not found.")
        return wein

    @auth_required(bp)
    @bp.arguments(WeinSchema)
    @bp.response(200, WeinSchema)
    def put(self, daten, wine_id):
        """Replace a wine recipe"""
        claims = get_jwt()
        if claims.get("rolle") not in ("user", "admin"):
            abort(403, message="Insufficient permissions.")
        wein = db.session.get(Wein, wine_id)
        if not wein:
            abort(404, message="Wine recipe not found.")
        for key, value in daten.items():
            setattr(wein, key, value)
        db.session.commit()
        return wein

    @auth_required(bp)
    @bp.arguments(WeinPatchSchema)
    @bp.response(200, WeinSchema)
    def patch(self, daten, wine_id):
        """Partially update a wine recipe"""
        claims = get_jwt()
        if claims.get("rolle") not in ("user", "admin"):
            abort(403, message="Insufficient permissions.")
        wein = db.session.get(Wein, wine_id)
        if not wein:
            abort(404, message="Wine recipe not found.")
        for key, value in daten.items():
            setattr(wein, key, value)
        db.session.commit()
        return wein

    @auth_required(bp)
    @bp.response(204)
    def delete(self, wine_id):
        """Delete a wine recipe (admin only)"""
        claims = get_jwt()
        if claims.get("rolle") != "admin":
            abort(403, message="Only administrators can delete wine recipes.")
        wein = db.session.get(Wein, wine_id)
        if not wein:
            abort(404, message="Wine recipe not found.")
        db.session.delete(wein)
        db.session.commit()
