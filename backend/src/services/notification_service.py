import boto3

from src.common.config import settings
from src.common.logger import get_logger
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.utils.time_utils import utc_now_iso

logger = get_logger(__name__)
_sns = boto3.client("sns", region_name=settings.region)
_notifications_repo = DynamoRepository(settings.notifications_table)


def send_sms(phone_number: str, message: str):
    _sns.publish(
        PhoneNumber=phone_number,
        Message=message,
        MessageAttributes={
            "AWS.SNS.SMS.SenderID": {"DataType": "String", "StringValue": settings.sns_sender_id}
        },
    )
    _notifications_repo.put(
        {
            "UUID": new_uuid(),
            "user_phone": phone_number,
            "message": message,
            "type": "SMS",
            "created_at": utc_now_iso(),
        }
    )
    logger.info("SMS sent to %s", phone_number)
