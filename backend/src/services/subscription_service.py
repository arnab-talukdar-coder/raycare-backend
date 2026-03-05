from src.common.config import settings
from src.common.exceptions import NotFoundError
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.utils.time_utils import utc_now_iso

subscriptions_repo = DynamoRepository(settings.subscriptions_table)


def purchase_subscription(patient_phone: str, payload: dict):
    item = {
        "UUID": new_uuid(),
        "patient_phone": patient_phone,
        "plan_name": payload["plan_name"],
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
        "status": "ACTIVE",
        "payment_status": payload.get("payment_status", "PAID"),
        "created_at": utc_now_iso(),
    }
    subscriptions_repo.put(item)
    return item


def get_subscription_status(patient_phone: str):
    items = [x for x in subscriptions_repo.scan() if x.get("patient_phone") == patient_phone]
    if not items:
        raise NotFoundError("No subscription found")
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items[0]
