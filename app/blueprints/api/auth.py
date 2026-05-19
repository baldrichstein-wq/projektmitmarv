from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from flask_smorest import Blueprint, abort

from app.models.benutzer import Benutzer
from app.extensions import db
from app.blueprints.api.decorators import auth_required
from app.schemas.benutzer import LoginSchema, TokenSchema

bp = Blueprint(
    "authentication", __name__, url_prefix="/api/v1/auth", description="Authentication"
)


@bp.route("/logi")
class Login(MethodView):
    @bp.arguments(LoginSchema)
    @bp.response(200, TokenSchema)
    def post(self, daten):
        """Authenticate user and issue JWT tokens"""
        benutzer = Benutzer.query.filter_by(email=daten["email"]).first()
        if not benutzer or not benutzer.check_password(daten["password"]):
            abort(401, message="Invalid credentials.")

        zusatz_claims = {"rolle": benutzer.rolle, "name": benutzer.name}
        access_token = create_access_token(
            identity=str(benutzer.id), additional_claims=zusatz_claims
        )
        refresh_token = create_refresh_token(identity=str(benutzer.id))
        return {"access_token": access_token, "refresh_token": refresh_token}


@bp.route("/refresh")
class Refresh(MethodView):
    @auth_required(bp, refresh=True)
    @bp.response(200, TokenSchema)
    def post(self):
        """Issue a new access token using a refresh token"""
        benutzer_id = get_jwt_identity()
        benutzer = (
            db.session.get(Benutzer, int(benutzer_id))
            if benutzer_id is not None
            else None
        )
        if not benutzer:
            abort(404, message="User not found.")
        zusatz_claims = {"rolle": benutzer.rolle, "name": benutzer.name}
        access_token = create_access_token(
            identity=str(benutzer_id), additional_claims=zusatz_claims
        )
        return {"access_token": access_token}
