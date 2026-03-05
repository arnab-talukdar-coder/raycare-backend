from src.common.api import dispatch, parse_body
from src.common.responses import ok
from src.services import auth_service
from src.utils.validators import require_fields


def send_otp_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["phone_number"])
    return ok(auth_service.send_otp(body["phone_number"]))


def verify_otp_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["phone_number", "otp_code"])
    return ok(auth_service.verify_otp(body["phone_number"], body["otp_code"]))


def register_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["phone_number", "user_name"])
    return ok(auth_service.register_patient(body), 201)


def logout_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["session_id"])
    return ok(auth_service.logout(body["session_id"]))


def lambda_handler(event, context):
    routes = {
        ("POST", "/auth/send-otp"): send_otp_handler,
        ("POST", "/auth/verify-otp"): verify_otp_handler,
        ("POST", "/auth/register"): register_handler,
        ("POST", "/auth/logout"): logout_handler,
    }
    return dispatch(event, routes)
