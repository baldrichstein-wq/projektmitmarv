from marshmallow import Schema, fields, validate

ROLLEN = ("gast", "benutzer", "admin")


class BenutzerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    rolle = fields.Str(dump_only=True, validate=validate.OneOf(ROLLEN))


class RolleUpdateSchema(Schema):
    rolle = fields.Str(required=True, validate=validate.OneOf(ROLLEN))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class TokenSchema(Schema):
    access_token = fields.Str(dump_only=True)
    refresh_token = fields.Str(dump_only=True)
