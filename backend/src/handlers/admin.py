from src.common.api import dispatch, parse_body
from src.common.constants import Role
from src.common.responses import ok
from src.middleware.auth import authorize
from src.services.service_request_service import assign_nurse, list_service_requests
from src.utils.validators import require_fields


@authorize([Role.ADMIN, Role.SUPER_ADMIN])
def service_requests(event, _ctx):
    return ok({"service_requests": list_service_requests()})


@authorize([Role.ADMIN, Role.SUPER_ADMIN])
def assign_nurse_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["service_request_id", "nurse_phone"])
    return ok(
        assign_nurse(
            body["service_request_id"],
            body["nurse_phone"],
            event["auth"]["phone_number"],
        )
    )


def lambda_handler(event, context):
    routes = {
        ("GET", "/admin/service-requests"): service_requests,
        ("POST", "/admin/assign-nurse"): assign_nurse_handler,
    }
    return dispatch(event, routes)
