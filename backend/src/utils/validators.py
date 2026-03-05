import re

from src.common.exceptions import AppError


PHONE_REGEX = re.compile(r"^\+?[1-9]\d{9,14}$")


def require_fields(data: dict, fields: list[str]):
    missing = [f for f in fields if f not in data or data[f] in (None, "")]
    if missing:
        raise AppError(f"Missing required fields: {', '.join(missing)}", 422)


def validate_phone(phone: str):
    if not PHONE_REGEX.match(phone):
        raise AppError("Invalid phone number format", 422)
