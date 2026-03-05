from src.common.config import settings
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.utils.time_utils import utc_now_iso

service_requests_repo = DynamoRepository(settings.service_requests_table)


def book_appointment(patient_phone: str, payload: dict):
    item = {
        "UUID": new_uuid(),
        "patient_phone": patient_phone,
        "service_uuid": payload.get("service_uuid", "DOCTOR_APPOINTMENT"),
        "status": "BOOKED",
        "assigned_nurse": "",
        "assigned_doctor": payload["doctor_phone"],
        "preferred_time": payload["appointment_time"],
        "created_at": utc_now_iso(),
        "notes": payload.get("notes", ""),
        "request_type": "APPOINTMENT",
    }
    service_requests_repo.put(item)
    return item


def list_patient_appointments(patient_phone: str):
    return [
        x
        for x in service_requests_repo.scan()
        if x.get("patient_phone") == patient_phone and x.get("request_type") == "APPOINTMENT"
    ]


def list_doctor_appointments(doctor_phone: str):
    return [
        x
        for x in service_requests_repo.scan()
        if x.get("assigned_doctor") == doctor_phone and x.get("request_type") == "APPOINTMENT"
    ]
