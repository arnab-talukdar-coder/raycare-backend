from src.common.config import settings
from src.common.constants import HealthEventType, ServiceRequestStatus
from src.common.exceptions import NotFoundError
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.services.notification_service import send_sms
from src.services.pdf_service import render_pdf
from src.services.storage_service import upload_bytes
from src.utils.time_utils import utc_now_iso

health_events_repo = DynamoRepository(settings.health_events_table)
service_requests_repo = DynamoRepository(settings.service_requests_table)


def list_patient_history(patient_phone: str):
    return [x for x in health_events_repo.scan() if x.get("patient_phone") == patient_phone]


def submit_nurse_visit_report(nurse_phone: str, payload: dict):
    request_id = payload["service_request_id"]
    req = service_requests_repo.get("UUID", request_id)
    if not req or req.get("assigned_nurse") != nurse_phone:
        raise NotFoundError("Assigned service request not found")

    lines = [
        f"Patient: {req['patient_phone']}",
        f"Nurse: {nurse_phone}",
        f"Visit Time: {utc_now_iso()}",
        f"Vitals: {payload.get('vitals', {})}",
        f"Measurements: {payload.get('measurements', {})}",
        f"Notes: {payload.get('notes', '')}",
    ]
    pdf = render_pdf("RayCare Nurse Visit Report", lines)
    key = f"patients/{req['patient_phone']}/reports/{request_id}.pdf"
    file_url = upload_bytes(pdf, key)

    event = {
        "UUID": new_uuid(),
        "patient_phone": req["patient_phone"],
        "event_type": HealthEventType.VISIT_REPORT.value,
        "event_time": utc_now_iso(),
        "metadata": {
            "service_request_id": request_id,
            "nurse_phone": nurse_phone,
            "notes": payload.get("notes", ""),
        },
        "file_url": file_url,
    }
    health_events_repo.put(event)
    req["status"] = ServiceRequestStatus.COMPLETED.value
    service_requests_repo.put(req)
    send_sms(req["patient_phone"], "Your nurse visit report is available in RayCare.")
    return event


def create_prescription_pdf(doctor_phone: str, payload: dict):
    patient_phone = payload["patient_phone"]
    lines = [
        f"Patient: {patient_phone}",
        f"Doctor: {doctor_phone}",
        f"Consultation Time: {utc_now_iso()}",
        "Medicines:",
    ]
    for med in payload.get("medications", []):
        lines.append(f"- {med.get('medicine_name')} | {med.get('dosage')} | {med.get('frequency')}")
    lines.append(f"Instructions: {payload.get('instructions', '')}")

    pdf = render_pdf("RayCare E-Prescription", lines)
    key = f"patients/{patient_phone}/prescriptions/{new_uuid()}.pdf"
    file_url = upload_bytes(pdf, key)
    event = {
        "UUID": new_uuid(),
        "patient_phone": patient_phone,
        "event_type": HealthEventType.PRESCRIPTION.value,
        "event_time": utc_now_iso(),
        "metadata": {
            "doctor_phone": doctor_phone,
            "medications": payload.get("medications", []),
            "instructions": payload.get("instructions", ""),
        },
        "file_url": file_url,
    }
    health_events_repo.put(event)
    send_sms(patient_phone, "Your RayCare prescription has been uploaded.")
    return event
