from src.common.config import settings
from src.common.exceptions import AppError
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.utils.time_utils import utc_now_iso

users_repo = DynamoRepository(settings.users_table)
services_repo = DynamoRepository(settings.services_table)
assignments_repo = DynamoRepository(settings.assignments_table)


def create_user(payload: dict):
    existing = users_repo.get("phone_number", payload["phone_number"], "user_name", payload["user_name"])
    if existing:
        raise AppError("User already exists", 409)
    item = {
        "phone_number": payload["phone_number"],
        "user_name": payload["user_name"],
        "role": payload["role"],
        "name": payload.get("name", payload["user_name"]),
        "age": payload.get("age"),
        "gender": payload.get("gender"),
        "address": payload.get("address"),
        "subscription_plan": payload.get("subscription_plan", "BASIC"),
        "created_at": utc_now_iso(),
    }
    users_repo.put(item)
    return item


def create_service(payload: dict):
    item = {
        "UUID": new_uuid(),
        "service_name": payload["service_name"],
        "service_type": payload["service_type"],
        "price": payload["price"],
    }
    services_repo.put(item)
    return item


def assign_doctor_to_patient(payload: dict):
    item = {
        "UUID": new_uuid(),
        "patient_phone": payload["patient_phone"],
        "nurse_phone": payload.get("nurse_phone", ""),
        "doctor_phone": payload["doctor_phone"],
        "assigned_at": utc_now_iso(),
    }
    assignments_repo.put(item)
    return item


def list_system_data():
    return {
        "users": users_repo.scan(),
        "services": services_repo.scan(),
        "assignments": assignments_repo.scan(),
    }
