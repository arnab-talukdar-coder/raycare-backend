from datetime import datetime

from src.common.config import settings
from src.repositories.dynamodb_client import DynamoRepository
from src.services.notification_service import send_sms

reminders_repo = DynamoRepository(settings.medication_reminders_table)


def add_medication_reminder(doctor_phone: str, payload: dict):
    item = {
        "UUID": payload.get("UUID"),
        "patient_phone": payload["patient_phone"],
        "medicine_name": payload["medicine_name"],
        "dosage": payload["dosage"],
        "reminder_times": payload["reminder_times"],
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
        "doctor_phone": doctor_phone,
    }
    if not item["UUID"]:
        from src.repositories.dynamodb_client import new_uuid

        item["UUID"] = new_uuid()
    reminders_repo.put(item)
    return item


def run_due_reminders(now: datetime | None = None):
    now = now or datetime.utcnow()
    now_date = now.date().isoformat()
    now_time = now.strftime("%H:%M")
    due = []
    for item in reminders_repo.scan():
        if item["start_date"] <= now_date <= item["end_date"] and now_time in item.get("reminder_times", []):
            due.append(item)
    for item in due:
        send_sms(
            item["patient_phone"],
            f"RayCare medicine reminder: {item['medicine_name']} ({item['dosage']})",
        )
    return {"checked": len(due)}
