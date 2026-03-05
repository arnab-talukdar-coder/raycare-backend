from src.common.api import dispatch, parse_body
from src.common.constants import Role
from src.common.responses import ok
from src.middleware.auth import authorize
from src.services.appointment_service import book_appointment, list_patient_appointments
from src.services.emergency_service import raise_sos
from src.services.medical_service import list_patient_history
from src.services.service_request_service import create_service_request
from src.services.user_service import get_user_by_phone, update_user_profile
from src.utils.validators import require_fields


@authorize([Role.PATIENT, Role.ADMIN, Role.SUPER_ADMIN])
def profile(event, _ctx):
    return ok(get_user_by_phone(event["auth"]["phone_number"]))


@authorize([Role.PATIENT])
def edit_profile(event, _ctx):
    body = parse_body(event)
    return ok(update_user_profile(event["auth"]["phone_number"], body))


@authorize([Role.PATIENT])
def raise_service(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["service_uuid"])
    return ok(create_service_request(event["auth"]["phone_number"], body), 201)


@authorize([Role.PATIENT])
def book_doctor_appointment(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["doctor_phone", "appointment_time"])
    return ok(book_appointment(event["auth"]["phone_number"], body), 201)


@authorize([Role.PATIENT, Role.ADMIN, Role.SUPER_ADMIN])
def appointments(event, _ctx):
    return ok({"appointments": list_patient_appointments(event["auth"]["phone_number"])})


@authorize([Role.PATIENT, Role.DOCTOR, Role.ADMIN, Role.SUPER_ADMIN])
def history(event, _ctx):
    phone = event["auth"]["phone_number"]
    query = event.get("queryStringParameters") or {}
    patient_phone = query.get("patient_phone", phone)
    return ok({"history": list_patient_history(patient_phone)})


@authorize([Role.PATIENT])
def sos(event, _ctx):
    return ok(raise_sos(event["auth"]["phone_number"]), 201)


def lambda_handler(event, context):
    routes = {
        ("GET", "/patient/profile"): profile,
        ("POST", "/patient/edit-profile"): edit_profile,
        ("POST", "/health/raise-service"): raise_service,
        ("POST", "/patient/book-appointment"): book_doctor_appointment,
        ("GET", "/patient/appointments"): appointments,
        ("GET", "/patient/history"): history,
        ("POST", "/health/sos"): sos,
    }
    return dispatch(event, routes)
