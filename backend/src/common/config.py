import os


class Settings:
    region = os.getenv("AWS_REGION", "us-east-1")
    jwt_secret = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_issuer = os.getenv("JWT_ISSUER", "raycare-api")
    jwt_exp_minutes = int(os.getenv("JWT_EXP_MINUTES", "60"))

    users_table = os.getenv("USERS_TABLE", "raycare-users")
    sessions_table = os.getenv("SESSIONS_TABLE", "raycare-sessions")
    services_table = os.getenv("SERVICES_TABLE", "raycare-services")
    service_requests_table = os.getenv("SERVICE_REQUESTS_TABLE", "raycare-service-requests")
    assignments_table = os.getenv("ASSIGNMENTS_TABLE", "raycare-assignments")
    health_events_table = os.getenv("HEALTH_EVENTS_TABLE", "raycare-health-events")
    emergency_cases_table = os.getenv("EMERGENCY_CASES_TABLE", "raycare-emergency-cases")
    notifications_table = os.getenv("NOTIFICATIONS_TABLE", "raycare-notifications")
    subscriptions_table = os.getenv("SUBSCRIPTIONS_TABLE", "raycare-subscriptions")
    medication_reminders_table = os.getenv("MEDICATION_REMINDERS_TABLE", "raycare-medication-reminders")

    medical_records_bucket = os.getenv("MEDICAL_RECORDS_BUCKET", "raycare-medical-records")
    sns_sender_id = os.getenv("SNS_SENDER_ID", "RayCare")
    sms_enabled = os.getenv("SMS_ENABLED", "true").lower() == "true"
    otp_debug_mode = os.getenv("OTP_DEBUG_MODE", "false").lower() == "true"


settings = Settings()
