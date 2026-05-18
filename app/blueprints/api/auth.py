from flask.views import MethodView
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

from app.models.benutzer import Benutzer
from app.schemas.benutzer import LoginSchema, TokenSchema

bp = Blueprint("api_auth", __name__, url_prefix="/api/v1/auth", description="Authentifizierung")


@bp.route("/login")
class Login(MethodView):
    @bp.arguments(LoginSchema)
    @bp.response(200, TokenSchema)
    def post(self, daten):
        """Anmelden und JWT-Token erhalten"""
        benutzer = Benutzer.query.filter_by(email=daten["email"]).first()
        if not benutzer or not benutzer.check_password(daten["password"]):
            abort(401, message="Ungültige Anmeldedaten.")

        zusatz_claims = {"rolle": benutzer.rolle, "name": benutzer.name}
        access_token = create_access_token(identity=str(benutzer.id), additional_claims=zusatz_claims)
        refresh_token = create_refresh_token(identity=str(benutzer.id))
        return {"access_token": access_token, "refresh_token": refresh_token}


@bp.route("/refresh")
class Refresh(MethodView):
    @jwt_required(refresh=True)
    @bp.response(200, TokenSchema)
    def post(self):
        """Access-Token mit Refresh-Token erneuern"""
        benutzer_id = get_jwt_identity()
        benutzer = Benutzer.query.get_or_404(int(benutzer_id))
        zusatz_claims = {"rolle": benutzer.rolle, "name": benutzer.name}
        access_token = create_access_token(identity=str(benutzer_id), additional_claims=zusatz_claims)
        return {"access_token": access_token}
