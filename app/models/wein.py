from ..extensions import db


class Wein(db.Model):
    __tablename__ = "wein"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    liter = db.Column(db.Float, nullable=False, default=5.0)
    zutaten = db.Column(db.JSON, nullable=False, default=list)
    beschreibung = db.Column(db.Text, nullable=True)
    brauanweisung = db.Column(db.Text, nullable=True)
    brauzeit = db.Column(db.Integer, nullable=True)  # in Wochen
    alkoholgehalt = db.Column(db.Float, nullable=True)  # in Prozent

    def __repr__(self) -> str:
        return f"<Wein {self.name}>"
