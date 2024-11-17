from typing import Optional
import boto3
from mypy_boto3_s3.client import S3Client


def upload_to_s3(
    file_path: str,
    bucket: Optional[str],
    content: str,
    region_name: Optional[str],
) -> None:
    """Upload a file to S3"""
    if not bucket:
        raise ValueError("Bucket is required")

    if not region_name:
        raise ValueError("Region name is required")

    s3_client: S3Client = boto3.client("s3", region_name=region_name)
    s3_client.put_object(Bucket=bucket, Key=file_path, Body=content)


def check_if_file_exists_in_s3(
    bucket: Optional[str], key: str, region_name: Optional[str]
) -> bool:
    """Check if a file exists in S3"""
    if not bucket:
        raise ValueError("Bucket is required")

    if not region_name:
        raise ValueError("Region name is required")

    s3_client: S3Client = boto3.client("s3", region_name=region_name)
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except Exception:
        return False
