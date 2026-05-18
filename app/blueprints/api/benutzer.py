from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.models.benutzer import Benutzer
from app.schemas.benutzer import BenutzerSchema, RolleUpdateSchema

bp = Blueprint("api_benutzer", __name__, url_prefix="/api/v1/benutzer", description="Benutzerverwaltung")


def _require_admin():
    claims = get_jwt()
    if claims.get("rolle") != "admin":
        abort(403, message="Nur Administratoren haben Zugriff.")


@bp.route("/")
class BenutzerListe(MethodView):
    @jwt_required()
    @bp.response(200, BenutzerSchema(many=True))
    def get(self):
        """Alle Benutzer abrufen (nur Admin)"""
        _require_admin()
        return Benutzer.query.all()


@bp.route("/<int:benutzer_id>/rolle")
class BenutzerRolle(MethodView):
    @jwt_required()
    @bp.arguments(RolleUpdateSchema)
    @bp.response(200, BenutzerSchema)
    def put(self, daten, benutzer_id):
        """Rolle eines Benutzers ändern (nur Admin)"""
        _require_admin()
        benutzer = Benutzer.query.get_or_404(benutzer_id)
        benutzer.rolle = daten["rolle"]
        db.session.commit()
        return benutzer
