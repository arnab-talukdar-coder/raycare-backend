import json
from typing import Callable

from src.common.exceptions import AppError
from src.common.logger import get_logger
from src.common.responses import error

logger = get_logger(__name__)


def parse_body(event: dict) -> dict:
    raw = event.get("body")
    if not raw:
        return {}
    if event.get("isBase64Encoded"):
        raise AppError("Base64 payloads are not supported", 415)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AppError("Invalid JSON body", 400) from exc


def dispatch(event: dict, routes: dict[tuple[str, str], Callable]):
    method = (event.get("requestContext", {}).get("http", {}).get("method") or "").upper()
    path = event.get("rawPath", "")
    handler = routes.get((method, path))
    if not handler:
        return error("Route not found", 404)
    try:
        return handler(event, None)
    except AppError as exc:
        return error(exc.message, exc.status_code)
    except Exception as exc:
        logger.exception("Unhandled error: %s", exc)
        return error("Internal server error", 500)
