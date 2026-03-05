from src.common.api import dispatch, parse_body
from src.common.constants import Role
from src.common.responses import ok
from src.middleware.auth import authorize
from src.services.appointment_service import list_doctor_appointments
from src.services.medical_service import create_prescription_pdf, list_patient_history
from src.services.reminder_service import add_medication_reminder
from src.utils.validators import require_fields


@authorize([Role.DOCTOR])
def doctor_appointments(event, _ctx):
    return ok({"appointments": list_doctor_appointments(event["auth"]["phone_number"])})


@authorize([Role.DOCTOR])
def generate_prescription(event, _ctx):
    body = parse_body(event)
    require_fields(body, ["patient_phone", "medications"])
    return ok(create_prescription_pdf(event["auth"]["phone_number"], body), 201)


@authorize([Role.DOCTOR])
def add_medication(event, _ctx):
    body = parse_body(event)
    require_fields(
        body,
        ["patient_phone", "medicine_name", "dosage", "reminder_times", "start_date", "end_date"],
    )
    return ok(add_medication_reminder(event["auth"]["phone_number"], body), 201)


@authorize([Role.DOCTOR, Role.ADMIN, Role.SUPER_ADMIN])
def patient_history(event, _ctx):
    query = event.get("queryStringParameters") or {}
    require_fields(query, ["patient_phone"])
    return ok({"history": list_patient_history(query["patient_phone"])})


def lambda_handler(event, context):
    routes = {
        ("GET", "/doctor/appointments"): doctor_appointments,
        ("POST", "/doctor/generate-prescription"): generate_prescription,
        ("POST", "/doctor/add-medication"): add_medication,
        ("GET", "/doctor/patient-history"): patient_history,
    }
    return dispatch(event, routes)
