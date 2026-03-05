from src.common.api import dispatch, parse_body
from src.common.constants import Role
from src.common.responses import ok
from src.middleware.auth import authorize
from src.services.admin_service import (
    assign_doctor_to_patient,
    create_service,
    create_user,
    list_system_data,
)
from src.services.service_request_service import list_service_requests
from src.services.user_service import list_users
from src.utils.validators import require_fields


@authorize([Role.SUPER_ADMIN])
def create_user_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["phone_number", "user_name", "role"])
    return ok(create_user(body), 201)


@authorize([Role.SUPER_ADMIN])
def assign_doctor(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["patient_phone", "doctor_phone"])
    return ok(assign_doctor_to_patient(body), 201)


@authorize([Role.SUPER_ADMIN])
def create_service_handler(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["service_name", "service_type", "price"])
    return ok(create_service(body), 201)


@authorize([Role.SUPER_ADMIN])
def all_users(event, _ctx):
    return ok({"users": list_users()})


@authorize([Role.SUPER_ADMIN])
def system_data(event, _ctx):
    data = list_system_data()
    data["service_requests"] = list_service_requests()
    return ok(data)


def lambda_handler(event, context):
    routes = {
        ("POST", "/superadmin/create-user"): create_user_handler,
        ("POST", "/superadmin/assign-doctor"): assign_doctor,
        ("POST", "/superadmin/create-service"): create_service_handler,
        ("GET", "/superadmin/all-users"): all_users,
        ("GET", "/superadmin/system-data"): system_data,
    }
    return dispatch(event, routes)
