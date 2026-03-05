# RayCare Backend (Serverless, AWS)

Production-oriented backend for RayCare using:
- API Gateway HTTP API
- AWS Lambda (Python)
- DynamoDB
- S3
- SNS SMS
- EventBridge Scheduler
- Terraform IaC
- JWT + RBAC
- ReportLab PDF generation

## Folder Structure

```text
backend/
  requirements.txt
  scripts/
    build_dependency_layer.ps1
  src/
    common/
    middleware/
    repositories/
    services/
    handlers/
    scheduler/
  terraform/
    main.tf
    providers.tf
    variables.tf
    outputs.tf
    terraform.tfvars.example
    modules/
      lambda/
      http_api/
```

## API Modules

- `src/handlers/auth.py`
- `src/handlers/patient.py`
- `src/handlers/nurse.py`
- `src/handlers/doctor.py`
- `src/handlers/admin.py`
- `src/handlers/super_admin.py`
- `src/handlers/subscription.py`
- `src/scheduler/medication_scheduler.py`

All handlers implement route dispatch for HTTP API v2 payloads.

## Security Model

- JWT Bearer auth using `HS256`.
- Role-based authorization middleware (`PATIENT`, `NURSE`, `DOCTOR`, `ADMIN`, `SUPER_ADMIN`).
- Least-privilege Lambda IAM role for DynamoDB/S3/SNS.
- S3 bucket has:
  - versioning enabled
  - server-side encryption enabled (AES256)
  - public access blocked

## Workflows Implemented

- OTP send/verify via SNS.
- Patient service request lifecycle.
- Nurse visit workflow with PDF generation and S3 upload.
- Doctor e-prescription workflow with PDF generation and patient SMS.
- SOS alerts to assigned nurse/admin with emergency case persistence.
- Medication reminders from EventBridge Scheduler every minute.
- Subscription purchase/status APIs.
- Super admin management APIs for user/service/assignments/system view.

## Terraform Deploy

1. Build and publish dependency Lambda Layer (required for `PyJWT` and `reportlab`):

```powershell
cd backend
.\scripts\build_dependency_layer.ps1
```

2. Create layer in AWS and copy Layer ARN.

3. Configure terraform variables:

```bash
cd backend/terraform
cp terraform.tfvars.example terraform.tfvars
```

Set:
- `jwt_secret`
- `dependency_layer_arn`
- `medical_records_bucket` (must be globally unique in AWS S3)

4. Apply:

```bash
terraform init
terraform plan
terraform apply
```

5. Use output `api_endpoint` as base URL.

## Required Environment Variables (set by Terraform)

- `JWT_SECRET`
- `JWT_ISSUER`
- `USERS_TABLE`
- `SESSIONS_TABLE`
- `SERVICES_TABLE`
- `SERVICE_REQUESTS_TABLE`
- `ASSIGNMENTS_TABLE`
- `HEALTH_EVENTS_TABLE`
- `EMERGENCY_CASES_TABLE`
- `NOTIFICATIONS_TABLE`
- `SUBSCRIPTIONS_TABLE`
- `MEDICATION_REMINDERS_TABLE`
- `MEDICAL_RECORDS_BUCKET`

## Notes for Production Hardening

- Replace OTP persistence scan logic with GSI-based queries.
- Add AWS WAF, custom domain, and API throttling.
- Add idempotency keys for write endpoints.
- Add alarms/dashboards (CloudWatch + X-Ray + DLQs).
- Add encrypted JWT secret from AWS Secrets Manager/SSM.
- Add integration and load tests in CI/CD pipeline.

## GitHub Auto Deploy

Workflow file: `.github/workflows/deploy-raycare.yml`

Required GitHub repository secrets:
- `AWS_ROLE_ARN` (OIDC role for GitHub Actions)
- `AWS_REGION` (example: `ap-south-1`)
- `JWT_SECRET` - iveoraRaycare
- `MEDICAL_RECORDS_BUCKET_NAME` (must be globally unique)raycare-medical-dev-bucket
