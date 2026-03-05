from src.common.api import dispatch, parse_body
from src.common.constants import Role
from src.common.responses import ok
from src.middleware.auth import authorize
from src.services.medical_service import submit_nurse_visit_report
from src.services.service_request_service import list_assigned_requests_for_nurse, start_visit
from src.utils.validators import require_fields


@authorize([Role.NURSE])
def assigned_services(event, _ctx):
    nurse_phone = event["auth"]["phone_number"]
    return ok({"services": list_assigned_requests_for_nurse(nurse_phone)})


@authorize([Role.NURSE])
def nurse_start_visit(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["service_request_id"])
    return ok(start_visit(event["auth"]["phone_number"], body["service_request_id"]))


@authorize([Role.NURSE])
def submit_visit(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["service_request_id"])
    return ok(submit_nurse_visit_report(event["auth"]["phone_number"], body), 201)


def lambda_handler(event, context):
    routes = {
        ("GET", "/nurse/assigned-services"): assigned_services,
        ("POST", "/nurse/start-visit"): nurse_start_visit,
        ("POST", "/nurse/submit-visit"): submit_visit,
    }
    return dispatch(event, routes)
