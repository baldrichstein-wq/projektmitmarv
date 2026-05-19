from collections.abc import Callable
from typing import Any

from flask_jwt_extended import jwt_required


def auth_required(bp, *, refresh: bool = False):
    """Combine OpenAPI security docs and JWT protection for API methods."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        wrapped = bp.doc(security=[{"bearerAuth": []}])(fn)
        return jwt_required(refresh=refresh)(wrapped)

    return decorator
