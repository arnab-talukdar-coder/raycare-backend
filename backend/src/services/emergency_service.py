from src.common.config import settings
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.services.notification_service import send_sms
from src.utils.time_utils import utc_now_iso

emergency_repo = DynamoRepository(settings.emergency_cases_table)
assignments_repo = DynamoRepository(settings.assignments_table)
users_repo = DynamoRepository(settings.users_table)


def raise_sos(patient_phone: str):
    case = {
        "UUID": new_uuid(),
        "patient_phone": patient_phone,
        "status": "OPEN",
        "created_at": utc_now_iso(),
        "resolved_at": "",
    }
    emergency_repo.put(case)

    assignments = [x for x in assignments_repo.scan() if x.get("patient_phone") == patient_phone]
    admins = [x for x in users_repo.scan() if x.get("role") in ("ADMIN", "SUPER_ADMIN")]
    if assignments:
        nurse_phone = assignments[-1].get("nurse_phone")
        if nurse_phone:
            send_sms(nurse_phone, f"SOS alert for patient {patient_phone}.")
    for admin in admins:
        send_sms(admin["phone_number"], f"SOS alert for patient {patient_phone}.")
    return case
