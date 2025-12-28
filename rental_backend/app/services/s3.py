from __future__ import annotations
from dataclasses import dataclass
from typing import IO, Optional

import boto3
from botocore.client import Config

from app.core.config import settings

@dataclass(frozen=True)
class S3ObjectRef:
    bucket: str
    key: str

def _client():
    # If keys are not set, boto3 will use instance role / env / shared config.
    kwargs = {"region_name": settings.AWS_REGION, "config": Config(signature_version="s3v4")}
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs.update(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return boto3.client("s3", **kwargs)

def build_key(*parts: str) -> str:
    prefix = (settings.S3_PREFIX or "").strip("/")
    clean_parts = [p.strip("/").replace("\\", "/") for p in parts if p and p.strip("/")]
    if prefix:
        return "/".join([prefix] + clean_parts)
    return "/".join(clean_parts)

def upload_fileobj(fileobj: IO[bytes], key: str, content_type: Optional[str] = None) -> S3ObjectRef:
    s3 = _client()
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    if extra:
        s3.upload_fileobj(fileobj, settings.S3_BUCKET, key, ExtraArgs=extra)
    else:
        s3.upload_fileobj(fileobj, settings.S3_BUCKET, key)
    return S3ObjectRef(bucket=settings.S3_BUCKET, key=key)

def presign_get(key: str, expires: Optional[int] = None) -> str:
    s3 = _client()
    exp = int(expires or settings.S3_PRESIGN_EXPIRE_SECONDS)
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=exp,
    )

def get_object_stream(key: str):
    s3 = _client()
    obj = s3.get_object(Bucket=settings.S3_BUCKET, Key=key)
    body = obj["Body"]
    content_type = obj.get("ContentType") or "application/octet-stream"
    return body, content_type
