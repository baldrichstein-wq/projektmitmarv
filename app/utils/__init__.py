def jwt_rolle() -> str:
    """Gibt die Rolle aus dem JWT-Cookie/-Header zurück (oder 'gast' wenn nicht angemeldet)."""
    try:
        from flask_jwt_extended import get_jwt
        return get_jwt().get("rolle", "gast")
    except Exception:
        return "gast"


def jwt_name() -> str:
    """Gibt den Namen aus dem JWT-Cookie/-Header zurück (oder 'Gast' wenn nicht angemeldet)."""
    try:
        from flask_jwt_extended import get_jwt
        return get_jwt().get("name", "Gast")
    except Exception:
        return "Gast"
