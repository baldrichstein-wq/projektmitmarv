from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()
jwt: JWTManager = JWTManager()
api: Api = Api()
