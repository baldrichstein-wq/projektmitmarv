import os

from dotenv import load_dotenv

load_dotenv()


def _resolve_database_uri() -> str:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgres://"):
        # SQLAlchemy erwartet postgresql:// statt postgres://
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        return url
    return "sqlite:///rezeptbuch.db"


class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-bitte-aendern")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-bitte-aendern")
    SQLALCHEMY_DATABASE_URI: str = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # flask-smorest / OpenAPI
    API_TITLE: str = "Rezeptbuch API"
    API_VERSION: str = "v1"
    OPENAPI_VERSION: str = "3.0.3"
    OPENAPI_URL_PREFIX: str = "/"
    OPENAPI_SWAGGER_UI_PATH: str = "/api/docs"
    OPENAPI_SWAGGER_UI_URL: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(Config):
    DEBUG: bool = True


class TestingConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False
    SECRET_KEY: str = "test-secret"
    JWT_SECRET_KEY: str = "test-jwt-secret"


class ProductionConfig(Config):
    DEBUG: bool = False
    JWT_COOKIE_SECURE: bool = True
    JWT_COOKIE_CSRF_PROTECT: bool = True


config: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
