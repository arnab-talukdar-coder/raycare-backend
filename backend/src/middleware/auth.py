from functools import wraps

from src.common.constants import Role
from src.common.exceptions import AppError, ForbiddenError, UnauthorizedError
from src.common.responses import error
from src.utils.jwt_utils import decode_jwt


def get_token_from_event(event: dict) -> str:
    headers = event.get("headers") or {}
    auth = headers.get("authorization") or headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise UnauthorizedError("Missing bearer token")
    return auth.split(" ", 1)[1].strip()


def authorize(allowed_roles: list[Role] | None = None):
    allowed_values = {r.value for r in (allowed_roles or [])}

    def decorator(func):
        @wraps(func)
        def wrapped(event, context):
            try:
                token = get_token_from_event(event)
                claims = decode_jwt(token)
                if allowed_values and claims.get("role") not in allowed_values:
                    raise ForbiddenError("Insufficient role permissions")
                event["auth"] = {
                    "phone_number": claims["sub"],
                    "role": claims["role"],
                }
                return func(event, context)
            except AppError as exc:
                return error(exc.message, exc.status_code)

        return wrapped

    return decorator
