from .benutzer import BenutzerSchema, LoginSchema, RolleUpdateSchema, TokenSchema
from .essen import EssenPatchSchema, EssenSchema
from .wein import WeinPatchSchema, WeinSchema

__all__ = [
    "BenutzerSchema",
    "LoginSchema",
    "RolleUpdateSchema",
    "TokenSchema",
    "EssenPatchSchema",
    "EssenSchema",
    "WeinPatchSchema",
    "WeinSchema",
]
