from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .lib import find_samconfig_path, load_stack_and_region
from .s3_object_ops import delete_public_index_html, upload_public_index_html
from .stack_outputs import describe_stack_outputs, get_stack_output_value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sam-s3",
        description="Utilities for operating objects in the SAM-created S3 bucket.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    outputs_parser = subparsers.add_parser(
        "outputs",
        help="Print CloudFormation stack outputs as JSON.",
    )
    outputs_parser.add_argument(
        "-e",
        "--environment",
        default="default",
        help="Environment name in samconfig.toml (default: default)",
    )

    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload HTML file to the stack S3 bucket.",
    )
    upload_parser.add_argument(
        "-s",
        "--source-path",
        default="public/index.html",
        help="Local HTML file path to upload (default: public/index.html)",
    )
    upload_parser.add_argument(
        "-k",
        "--object-key",
        default="index.html",
        help="S3 object key (default: index.html)",
    )
    upload_parser.add_argument(
        "-e",
        "--environment",
        default="default",
        help="Environment name in samconfig.toml (default: default)",
    )

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete an object from the stack S3 bucket.",
    )
    delete_parser.add_argument(
        "-k",
        "--object-key",
        default="index.html",
        help="S3 object key to delete (default: index.html)",
    )
    delete_parser.add_argument(
        "-e",
        "--environment",
        default="default",
        help="Environment name in samconfig.toml (default: default)",
    )

    return parser


def _run_outputs(environment: str) -> int:
    config_path = find_samconfig_path()
    stack_name, region = load_stack_and_region(config_path, environment=environment)
    outputs = describe_stack_outputs(stack_name=stack_name, region=region)
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    return 0


def _run_upload(source_path: str, object_key: str, environment: str) -> int:
    response = upload_public_index_html(
        source_path=Path(source_path),
        object_key=object_key,
        environment=environment,
    )

    config_path = find_samconfig_path()
    stack_name, region = load_stack_and_region(config_path, environment=environment)
    https_endpoint = get_stack_output_value(
        stack_name=stack_name,
        region=region,
        output_key="TestS3BucketHttpsEndpoint",
    )
    object_path = object_key.lstrip("/")
    object_url = f"{https_endpoint.rstrip('/')}/{object_path}"

    print(json.dumps(_json_safe_response(response), indent=2, ensure_ascii=False))
    print(object_url)
    return 0


def _run_delete(object_key: str, environment: str) -> int:
    response = delete_public_index_html(
        object_key=object_key,
        environment=environment,
    )
    print(json.dumps(_json_safe_response(response), indent=2, ensure_ascii=False))
    return 0


def _json_safe_response(response: dict[str, Any]) -> dict[str, Any]:
    response_metadata = response.get("ResponseMetadata")
    if not isinstance(response_metadata, dict):
        return response

    headers = response_metadata.get("HTTPHeaders")
    if isinstance(headers, dict):
        response_metadata["HTTPHeaders"] = {
            str(key): str(value) for key, value in headers.items()
        }
    return response


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "outputs":
        return _run_outputs(environment=args.environment)
    if args.command == "upload":
        return _run_upload(
            source_path=args.source_path,
            object_key=args.object_key,
            environment=args.environment,
        )
    if args.command == "delete":
        return _run_delete(
            object_key=args.object_key,
            environment=args.environment,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2
