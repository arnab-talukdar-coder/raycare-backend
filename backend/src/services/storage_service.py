import boto3

from src.common.config import settings

_s3 = boto3.client("s3", region_name=settings.region)


def upload_bytes(file_bytes: bytes, key: str, content_type: str = "application/pdf") -> str:
    _s3.put_object(
        Bucket=settings.medical_records_bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"s3://{settings.medical_records_bucket}/{key}"
