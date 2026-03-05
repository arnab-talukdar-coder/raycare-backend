from src.common.config import settings
from src.common.exceptions import NotFoundError
from src.repositories.dynamodb_client import DynamoRepository

users_repo = DynamoRepository(settings.users_table)


def get_user_by_phone(phone_number: str):
    users = users_repo.scan()
    user = next((x for x in users if x.get("phone_number") == phone_number), None)
    if not user:
        raise NotFoundError("User not found")
    return user


def update_user_profile(phone_number: str, patch: dict):
    user = get_user_by_phone(phone_number)
    updatable = ["name", "age", "gender", "address", "subscription_plan"]
    for key in updatable:
        if key in patch:
            user[key] = patch[key]
    users_repo.put(user)
    return user


def list_users(role: str | None = None):
    users = users_repo.scan()
    if role:
        return [u for u in users if u.get("role") == role]
    return users
