from src.common.api import dispatch, parse_body
from src.common.constants import Role
from src.common.responses import ok
from src.middleware.auth import authorize
from src.services.subscription_service import get_subscription_status, purchase_subscription
from src.utils.validators import require_fields


@authorize([Role.PATIENT, Role.ADMIN, Role.SUPER_ADMIN])
def purchase(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["plan_name", "start_date", "end_date"])
    return ok(purchase_subscription(event["auth"]["phone_number"], body), 201)


@authorize([Role.PATIENT, Role.ADMIN, Role.SUPER_ADMIN])
def status(event, _ctx):
    query = event.get("queryStringParameters") or {}
    phone = query.get("patient_phone", event["auth"]["phone_number"])
    return ok(get_subscription_status(phone))


def lambda_handler(event, context):
    routes = {
        ("POST", "/subscription/purchase"): purchase,
        ("GET", "/subscription/status"): status,
    }
    return dispatch(event, routes)
