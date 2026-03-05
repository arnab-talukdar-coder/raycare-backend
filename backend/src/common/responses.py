import json
from typing import Any, Dict


def ok(body: Dict[str, Any], status_code: int = 200):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def error(message: str, status_code: int = 400):
    return ok({"error": message}, status_code)
