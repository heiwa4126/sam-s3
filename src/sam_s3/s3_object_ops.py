from __future__ import annotations

from pathlib import Path
from typing import Any

import boto3

from .lib import find_samconfig_path, load_stack_and_region
from .stack_outputs import get_stack_output_value


def resolve_stack_bucket_name(
    output_key: str = "TestS3BucketName", environment: str = "default"
) -> tuple[str, str]:
    config_path = find_samconfig_path()
    stack_name, region = load_stack_and_region(config_path, environment=environment)
    bucket_name = get_stack_output_value(
        stack_name=stack_name,
        region=region,
        output_key=output_key,
    )
    return bucket_name, region


def upload_public_index_html(
    source_path: str | Path = "public/index.html",
    object_key: str = "index.html",
    environment: str = "default",
) -> dict[str, Any]:
    config_path = find_samconfig_path()
    project_root = config_path.parent
    local_path = Path(source_path)
    if not local_path.is_absolute():
        local_path = project_root / local_path

    if not local_path.exists():
        raise FileNotFoundError(f"Upload source file was not found: {local_path}")

    bucket_name, region = resolve_stack_bucket_name(environment=environment)
    s3_client = boto3.client("s3", region_name=region)

    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=local_path.read_bytes(),
        ContentType="text/html; charset=utf-8",
    )
    return response


def delete_public_index_html(
    object_key: str = "index.html",
    environment: str = "default",
) -> dict[str, Any]:
    bucket_name, region = resolve_stack_bucket_name(environment=environment)
    s3_client = boto3.client("s3", region_name=region)
    response = s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    return response


__all__ = [
    "resolve_stack_bucket_name",
    "upload_public_index_html",
    "delete_public_index_html",
]
