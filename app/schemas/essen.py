from marshmallow import Schema, fields, validate


class EssenSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    personenanzahl = fields.Int(load_default=2, validate=validate.Range(min=1))
    zutaten = fields.List(fields.Str(), load_default=list)
    beschreibung = fields.Str(load_default=None, allow_none=True)
    kochanweisung = fields.Str(load_default=None, allow_none=True)
    kochzeit = fields.Int(load_default=0, validate=validate.Range(min=0))
    kochzeit_formatiert = fields.Str(dump_only=True)


class EssenPatchSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    personenanzahl = fields.Int(validate=validate.Range(min=1))
    zutaten = fields.List(fields.Str())
    beschreibung = fields.Str(allow_none=True)
    kochanweisung = fields.Str(allow_none=True)
    kochzeit = fields.Int(validate=validate.Range(min=0))
