from marshmallow import Schema, fields, validate


class WeinSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    liter = fields.Float(load_default=5.0, validate=validate.Range(min=0.1))
    zutaten = fields.List(fields.Str(), load_default=list)
    beschreibung = fields.Str(load_default=None, allow_none=True)
    brauanweisung = fields.Str(load_default=None, allow_none=True)
    brauzeit = fields.Int(load_default=0, validate=validate.Range(min=0))
    alkoholgehalt = fields.Float(load_default=0.0, validate=validate.Range(min=0.0))
