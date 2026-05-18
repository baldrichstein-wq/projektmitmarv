from ..extensions import db


def format_kochzeit(minuten_gesamt: int) -> str:
    if not minuten_gesamt or minuten_gesamt <= 0:
        return "0 Min."
    stunden = minuten_gesamt // 60
    minuten = minuten_gesamt % 60
    parts = []
    if stunden > 0:
        parts.append(f"{stunden} Std.")
    if minuten > 0:
        parts.append(f"{minuten} Min.")
    return " ".join(parts)


class Essen(db.Model):
    __tablename__ = "essen"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    personenanzahl = db.Column(db.Integer, nullable=False, default=2)
    zutaten = db.Column(db.JSON, nullable=False, default=list)
    beschreibung = db.Column(db.Text, nullable=True)
    kochanweisung = db.Column(db.Text, nullable=True)
    kochzeit = db.Column(db.Integer, nullable=True)  # in Minuten

    @property
    def kochzeit_formatiert(self) -> str:
        return format_kochzeit(self.kochzeit)

    def __repr__(self) -> str:
        return f"<Essen {self.name}>"
