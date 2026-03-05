from src.common.config import settings
from src.common.constants import Role
from src.common.exceptions import AppError, UnauthorizedError
from src.repositories.dynamodb_client import DynamoRepository, new_uuid
from src.services.notification_service import send_sms
from src.utils.jwt_utils import create_jwt
from src.utils.otp_utils import generate_otp
from src.utils.time_utils import epoch_now, epoch_plus_minutes, utc_now_iso
from src.utils.validators import validate_phone

users_repo = DynamoRepository(settings.users_table)
sessions_repo = DynamoRepository(settings.sessions_table)


def send_otp(phone_number: str):
    validate_phone(phone_number)
    otp = generate_otp()
    sessions_repo.put(
        {
            "session_id": new_uuid(),
            "phone_number": phone_number,
            "otp_code": otp,
            "expires_at": epoch_plus_minutes(10),
            "created_at": utc_now_iso(),
            "session_type": "OTP",
        }
    )
    send_sms(phone_number, f"Your RayCare OTP is {otp}. Valid for 10 minutes.")
    return {"message": "OTP sent"}


def verify_otp(phone_number: str, otp_code: str):
    items = sessions_repo.scan()
    record = next(
        (
            x
            for x in items
            if x.get("phone_number") == phone_number
            and x.get("otp_code") == otp_code
            and x.get("session_type") == "OTP"
            and x.get("expires_at", 0) >= epoch_now()
        ),
        None,
    )
    if not record:
        raise UnauthorizedError("Invalid or expired OTP")
    users = users_repo.scan()
    user = next((x for x in users if x.get("phone_number") == phone_number), None)
    role = user.get("role", Role.PATIENT.value) if user else Role.PATIENT.value
    return {"token": create_jwt(phone_number, role), "role": role}


def register_patient(payload: dict):
    phone = payload["phone_number"]
    validate_phone(phone)
    if users_repo.get("phone_number", phone, "user_name", payload["user_name"]):
        raise AppError("User already exists", 409)
    item = {
        "phone_number": phone,
        "user_name": payload["user_name"],
        "role": Role.PATIENT.value,
        "name": payload.get("name", payload["user_name"]),
        "age": payload.get("age"),
        "gender": payload.get("gender"),
        "address": payload.get("address"),
        "subscription_plan": payload.get("subscription_plan", "BASIC"),
        "created_at": utc_now_iso(),
    }
    users_repo.put(item)
    return {"user": item}


def logout(session_id: str):
    sessions_repo.update(
        key={"session_id": session_id},
        update_expression="SET #expires_at = :exp",
        names={"#expires_at": "expires_at"},
        values={":exp": 0},
    )
    return {"message": "Logged out"}
