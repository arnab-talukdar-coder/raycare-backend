from enum import Enum


class Role(str, Enum):
    PATIENT = "PATIENT"
    NURSE = "NURSE"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class ServiceRequestStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class HealthEventType(str, Enum):
    VISIT_REPORT = "VISIT_REPORT"
    PRESCRIPTION = "PRESCRIPTION"
    SCAN = "SCAN"
