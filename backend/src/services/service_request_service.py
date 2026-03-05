from src.common.config import settings
from src.common.constants import ServiceRequestStatus
from src.common.exceptions import NotFoundError
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.services.notification_service import send_sms
from src.utils.time_utils import utc_now_iso

service_requests_repo = DynamoRepository(settings.service_requests_table)
assignments_repo = DynamoRepository(settings.assignments_table)


def create_service_request(patient_phone: str, payload: dict):
    item = {
        "UUID": new_uuid(),
        "patient_phone": patient_phone,
        "service_uuid": payload["service_uuid"],
        "status": ServiceRequestStatus.CREATED.value,
        "assigned_nurse": "",
        "assigned_doctor": "",
        "preferred_time": payload.get("preferred_time"),
        "created_at": utc_now_iso(),
        "notes": payload.get("notes", ""),
    }
    service_requests_repo.put(item)
    return item


def list_service_requests():
    return service_requests_repo.scan()


def list_assigned_requests_for_nurse(nurse_phone: str):
    return [x for x in service_requests_repo.scan() if x.get("assigned_nurse") == nurse_phone]


def start_visit(nurse_phone: str, request_id: str):
    req = service_requests_repo.get("UUID", request_id)
    if not req or req.get("assigned_nurse") != nurse_phone:
        raise NotFoundError("Assigned service request not found")
    req["status"] = ServiceRequestStatus.IN_PROGRESS.value
    service_requests_repo.put(req)
    return req


def assign_nurse(request_id: str, nurse_phone: str, admin_phone: str):
    req = service_requests_repo.get("UUID", request_id)
    if not req:
        raise NotFoundError("Service request not found")
    req["assigned_nurse"] = nurse_phone
    req["status"] = ServiceRequestStatus.ASSIGNED.value
    service_requests_repo.put(req)
    assignments_repo.put(
        {
            "UUID": new_uuid(),
            "patient_phone": req["patient_phone"],
            "nurse_phone": nurse_phone,
            "doctor_phone": req.get("assigned_doctor", ""),
            "assigned_at": utc_now_iso(),
            "assigned_by": admin_phone,
        }
    )
    send_sms(nurse_phone, f"You have been assigned a RayCare service request: {request_id}.")
    return req
