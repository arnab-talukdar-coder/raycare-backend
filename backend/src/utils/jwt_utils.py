from datetime import datetime, timedelta, timezone

import jwt

from src.common.config import settings
from src.common.exceptions import UnauthorizedError


def create_jwt(phone_number: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": phone_number,
        "role": role,
        "iss": settings.jwt_issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid token") from exc
