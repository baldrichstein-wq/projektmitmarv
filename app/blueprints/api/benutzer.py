from flask.views import MethodView
from flask_jwt_extended import get_jwt, get_jwt_identity
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.blueprints.api.decorators import auth_required
from app.models.benutzer import Benutzer
from app.schemas.benutzer import BenutzerCreateSchema, BenutzerSchema, RolleUpdateSchema

bp = Blueprint(
    "users", __name__, url_prefix="/api/v1/users", description="User management"
)


def _require_admin():
    claims = get_jwt()
    if claims.get("rolle") != "admin":
        abort(403, message="Only administrators can access this endpoint.")


@bp.route("/")
class BenutzerListe(MethodView):
    @auth_required(bp)
    @bp.response(200, BenutzerSchema(many=True))
    def get(self):
        """List all users (admin only)"""
        _require_admin()
        return Benutzer.query.all()

    @auth_required(bp)
    @bp.arguments(BenutzerCreateSchema)
    @bp.response(201, BenutzerSchema)
    def post(self, daten):
        """Create a new user (admin only)"""
        _require_admin()
        if Benutzer.query.filter_by(email=daten["email"]).first():
            abort(409, message="Email already in use.")

        neuer_benutzer = Benutzer(
            name=daten["name"],
            email=daten["email"],
            rolle=daten.get("rolle", "benutzer"),
        )
        neuer_benutzer.set_password(daten["password"])
        db.session.add(neuer_benutzer)
        db.session.commit()
        return neuer_benutzer


@bp.route("/<int:user_id>")
class BenutzerRolle(MethodView):
    @auth_required(bp)
    @bp.response(200, BenutzerSchema)
    def get(self, user_id):
        """Get a user by id (admin only)"""
        _require_admin()
        benutzer = db.session.get(Benutzer, user_id)
        if not benutzer:
            abort(404, message="User not found.")
        return benutzer

    @auth_required(bp)
    @bp.arguments(RolleUpdateSchema)
    @bp.response(200, BenutzerSchema)
    def patch(self, daten, user_id):
        """Partially update a user (role only, admin only)"""
        _require_admin()
        benutzer = db.session.get(Benutzer, user_id)
        if not benutzer:
            abort(404, message="User not found.")
        benutzer.rolle = daten["rolle"]
        db.session.commit()
        return benutzer

    @auth_required(bp)
    @bp.response(204)
    def delete(self, user_id):
        """Delete a user (admin only, cannot delete self)"""
        _require_admin()
        current_user_id = get_jwt_identity()
        if current_user_id is not None and int(current_user_id) == user_id:
            abort(403, message="You cannot delete your own account.")

        benutzer = db.session.get(Benutzer, user_id)
        if not benutzer:
            abort(404, message="User not found.")

        db.session.delete(benutzer)
        db.session.commit()
