from flask.views import MethodView
from flask_jwt_extended import get_jwt
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.blueprints.api.decorators import auth_required
from app.models.essen import Essen
from app.schemas.essen import EssenPatchSchema, EssenSchema

bp = Blueprint(
    "foods", __name__, url_prefix="/api/v1/foods", description="Food recipes"
)


@bp.route("/")
class EssenListe(MethodView):
    @auth_required(bp)
    @bp.response(200, EssenSchema(many=True))
    def get(self):
        """List all food recipes"""
        return Essen.query.all()

    @auth_required(bp)
    @bp.arguments(EssenSchema)
    @bp.response(201, EssenSchema)
    def post(self, daten):
        """Create a new food recipe"""
        claims = get_jwt()
        if claims.get("rolle") not in ("user", "admin"):
            abort(403, message="Insufficient permissions.")
        neues_essen = Essen(**daten)
        db.session.add(neues_essen)
        db.session.commit()
        return neues_essen


@bp.route("/<int:food_id>")
class EssenDetail(MethodView):
    @auth_required(bp)
    @bp.response(200, EssenSchema)
    def get(self, food_id):
        """Get a single food recipe"""
        essen = db.session.get(Essen, food_id)
        if not essen:
            abort(404, message="Food recipe not found.")
        return essen

    @auth_required(bp)
    @bp.arguments(EssenSchema)
    @bp.response(200, EssenSchema)
    def put(self, daten, food_id):
        """Replace a food recipe"""
        claims = get_jwt()
        if claims.get("rolle") not in ("user", "admin"):
            abort(403, message="Insufficient permissions.")
        essen = db.session.get(Essen, food_id)
        if not essen:
            abort(404, message="Food recipe not found.")
        for key, value in daten.items():
            setattr(essen, key, value)
        db.session.commit()
        return essen

    @auth_required(bp)
    @bp.arguments(EssenPatchSchema)
    @bp.response(200, EssenSchema)
    def patch(self, daten, food_id):
        """Partially update a food recipe"""
        claims = get_jwt()
        if claims.get("rolle") not in ("user", "admin"):
            abort(403, message="Insufficient permissions.")
        essen = db.session.get(Essen, food_id)
        if not essen:
            abort(404, message="Food recipe not found.")
        for key, value in daten.items():
            setattr(essen, key, value)
        db.session.commit()
        return essen

    @auth_required(bp)
    @bp.response(204)
    def delete(self, food_id):
        """Delete a food recipe (admin only)"""
        claims = get_jwt()
        if claims.get("rolle") != "admin":
            abort(403, message="Only administrators can delete recipes.")
        essen = db.session.get(Essen, food_id)
        if not essen:
            abort(404, message="Food recipe not found.")
        db.session.delete(essen)
        db.session.commit()
