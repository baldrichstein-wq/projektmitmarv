from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db

RECHTE_PRO_ROLLE: dict[str, list[str]] = {
    "admin": ["lesen", "schreiben", "aendern", "loeschen", "benutzer_verwalten"],
    "user": ["lesen", "schreiben", "aendern"],
    "gast": ["lesen"],
}


class Benutzer(db.Model):
    __tablename__ = "benutzer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    rolle = db.Column(db.String(20), nullable=False, default="user")

    def set_password(self, passwort: str) -> None:
        self.password_hash = generate_password_hash(passwort)

    def check_password(self, passwort: str) -> bool:
        return check_password_hash(self.password_hash, passwort)

    @property
    def rechte(self) -> list[str]:
        return RECHTE_PRO_ROLLE.get(self.rolle, RECHTE_PRO_ROLLE["gast"])

    def hat_recht(self, recht: str) -> bool:
        return recht in self.rechte

    def ist_admin(self) -> bool:
        return self.rolle == "admin"

    def __repr__(self) -> str:
        return f"<Benutzer {self.email} ({self.rolle})>"
