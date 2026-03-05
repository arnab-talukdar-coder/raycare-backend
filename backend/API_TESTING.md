# RayCare API Documentation and Testing Guide

This document matches the current backend implementation in `src/handlers/*`.

## 1. Base URL and Auth

- Base URL: use CloudFormation output `ApiEndpoint` (SAM) or Terraform output `api_endpoint`.
- Auth header for protected routes:

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

- Roles:
  - `PATIENT`
  - `NURSE`
  - `DOCTOR`
  - `ADMIN`
  - `SUPER_ADMIN`

## 2. OTP Testing Mode (No SMS Provider)

Current deployment is configured for testing:
- `SMS_ENABLED=false`
- `OTP_DEBUG_MODE=true`

`POST /auth/send-otp` returns `otp_code` in response.

OTP is also stored in DynamoDB `sessions` table with:
- `phone_number`
- `otp_code`
- `expires_at`
- `session_type=OTP`

## 3. Quick Start Test Flow

1. Register a patient.
2. Send OTP.
3. Verify OTP and capture JWT.
4. Call patient endpoints using that JWT.
5. Create admin/superadmin/doctor/nurse users via superadmin token for role testing.

---

## 4. API Reference

## Auth

### POST `/auth/register`
Public endpoint.

Body:
```json
{
  "phone_number": "+911234567890",
  "user_name": "john_patient",
  "name": "John",
  "age": 72,
  "gender": "M",
  "address": "Kolkata",
  "subscription_plan": "BASIC"
}
```

### POST `/auth/send-otp`
Public endpoint.

Body:
```json
{
  "phone_number": "+911234567890"
}
```

### POST `/auth/verify-otp`
Public endpoint.

Body:
```json
{
  "phone_number": "+911234567890",
  "otp_code": "123456"
}
```

Response:
```json
{
  "token": "<jwt>",
  "role": "PATIENT"
}
```

### POST `/auth/logout`
Public endpoint (expects session id in body).

Body:
```json
{
  "session_id": "<session-uuid>"
}
```

## Patient

### GET `/patient/profile`
Roles: `PATIENT`, `ADMIN`, `SUPER_ADMIN`

### POST `/patient/edit-profile`
Roles: `PATIENT`

Body (any subset):
```json
{
  "name": "John Updated",
  "age": 73,
  "gender": "M",
  "address": "New Address",
  "subscription_plan": "PREMIUM"
}
```

### POST `/health/raise-service`
Roles: `PATIENT`

Body:
```json
{
  "service_uuid": "service-uuid",
  "preferred_time": "2026-03-06T11:00:00Z",
  "notes": "Need BP check"
}
```

### POST `/patient/book-appointment`
Roles: `PATIENT`

Body:
```json
{
  "doctor_phone": "+919999999999",
  "appointment_time": "2026-03-07T10:30:00Z",
  "notes": "Follow-up"
}
```

### GET `/patient/appointments`
Roles: `PATIENT`, `ADMIN`, `SUPER_ADMIN`

### GET `/patient/history`
Roles: `PATIENT`, `DOCTOR`, `ADMIN`, `SUPER_ADMIN`

Optional query:
- `patient_phone` (used by doctor/admin/superadmin)

Example:
`/patient/history?patient_phone=+911234567890`

### POST `/health/sos`
Roles: `PATIENT`

No body required.

## Nurse

### GET `/nurse/assigned-services`
Roles: `NURSE`

### POST `/nurse/start-visit`
Roles: `NURSE`

Body:
```json
{
  "service_request_id": "request-uuid"
}
```

### POST `/nurse/submit-visit`
Roles: `NURSE`

Body:
```json
{
  "service_request_id": "request-uuid",
  "vitals": {
    "bp": "120/80",
    "pulse": 72
  },
  "measurements": {
    "sugar": "110 mg/dL"
  },
  "notes": "Patient stable"
}
```

This generates a PDF, uploads to S3, stores a health event, and marks request completed.

## Doctor

### GET `/doctor/appointments`
Roles: `DOCTOR`

### POST `/doctor/generate-prescription`
Roles: `DOCTOR`

Body:
```json
{
  "patient_phone": "+911234567890",
  "medications": [
    {
      "medicine_name": "Amlodipine",
      "dosage": "5mg",
      "frequency": "Once daily"
    }
  ],
  "instructions": "Take after breakfast"
}
```

### POST `/doctor/add-medication`
Roles: `DOCTOR`

Body:
```json
{
  "patient_phone": "+911234567890",
  "medicine_name": "Metformin",
  "dosage": "500mg",
  "reminder_times": ["08:00", "20:00"],
  "start_date": "2026-03-06",
  "end_date": "2026-03-20"
}
```

### GET `/doctor/patient-history`
Roles: `DOCTOR`, `ADMIN`, `SUPER_ADMIN`

Required query:
- `patient_phone`

Example:
`/doctor/patient-history?patient_phone=+911234567890`

## Admin

### GET `/admin/service-requests`
Roles: `ADMIN`, `SUPER_ADMIN`

### POST `/admin/assign-nurse`
Roles: `ADMIN`, `SUPER_ADMIN`

Body:
```json
{
  "service_request_id": "request-uuid",
  "nurse_phone": "+918888888888"
}
```

## Super Admin

### POST `/superadmin/create-user`
Roles: `SUPER_ADMIN`

Body:
```json
{
  "phone_number": "+919777777777",
  "user_name": "dr_sen",
  "role": "DOCTOR",
  "name": "Dr Sen",
  "age": 45,
  "gender": "F",
  "address": "Kolkata",
  "subscription_plan": "NA"
}
```

### POST `/superadmin/assign-doctor`
Roles: `SUPER_ADMIN`

Body:
```json
{
  "patient_phone": "+911234567890",
  "doctor_phone": "+919777777777",
  "nurse_phone": "+918888888888"
}
```

### POST `/superadmin/create-service`
Roles: `SUPER_ADMIN`

Body:
```json
{
  "service_name": "BP Check",
  "service_type": "HOME_VISIT",
  "price": 300
}
```

### GET `/superadmin/all-users`
Roles: `SUPER_ADMIN`

### GET `/superadmin/system-data`
Roles: `SUPER_ADMIN`

## Subscriptions

### POST `/subscription/purchase`
Roles: `PATIENT`, `ADMIN`, `SUPER_ADMIN`

Body:
```json
{
  "plan_name": "GOLD",
  "start_date": "2026-03-06",
  "end_date": "2027-03-05",
  "payment_status": "PAID"
}
```

### GET `/subscription/status`
Roles: `PATIENT`, `ADMIN`, `SUPER_ADMIN`

Optional query:
- `patient_phone`

---

## 5. curl Examples

Set once:

```bash
export BASE_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod"
```

Register:
```bash
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+911234567890","user_name":"john_patient"}'
```

Send OTP:
```bash
curl -X POST "$BASE_URL/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+911234567890"}'
```

Verify OTP:
```bash
curl -X POST "$BASE_URL/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+911234567890","otp_code":"123456"}'
```

Use token:
```bash
export TOKEN="<jwt-from-verify-otp>"
curl "$BASE_URL/patient/profile" -H "Authorization: Bearer $TOKEN"
```

Create service request:
```bash
curl -X POST "$BASE_URL/health/raise-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_uuid":"<service-uuid>","notes":"Need nurse visit"}'
```

---

## 6. Expected Error Patterns

- `401` when token is missing/invalid.
- `403` when role is not allowed.
- `404` for unknown route or resource not found.
- `422` for missing required fields or invalid phone.
- `500` for unhandled server errors.

Response format:
```json
{
  "error": "message"
}
```
