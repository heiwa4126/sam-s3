from __future__ import annotations

import json
from typing import Any

import boto3

from .lib import find_samconfig_path, load_stack_and_region


def describe_stack_outputs(stack_name: str, region: str) -> list[dict[str, Any]]:
    client = boto3.client("cloudformation", region_name=region)
    response = client.describe_stacks(StackName=stack_name)
    stacks = response.get("Stacks", [])
    if not stacks:
        return []
    return stacks[0].get("Outputs", [])


def get_stack_output_value(
    stack_name: str,
    region: str,
    output_key: str,
) -> str:
    outputs = describe_stack_outputs(stack_name=stack_name, region=region)
    matched = [output for output in outputs if output.get("OutputKey") == output_key]
    if not matched:
        raise KeyError(
            f"Output key '{output_key}' was not found in stack '{stack_name}'"
        )

    output_value = matched[0].get("OutputValue")
    if not isinstance(output_value, str) or output_value == "":
        raise ValueError(
            f"Output key '{output_key}' in stack '{stack_name}' does not have a valid value"
        )

    return output_value


def main() -> None:
    config_path = find_samconfig_path()
    stack_name, region = load_stack_and_region(config_path)
    outputs = describe_stack_outputs(stack_name=stack_name, region=region)
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
