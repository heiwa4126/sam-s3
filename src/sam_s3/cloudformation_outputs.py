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


def main() -> None:
    config_path = find_samconfig_path()
    stack_name, region = load_stack_and_region(config_path)
    outputs = describe_stack_outputs(stack_name=stack_name, region=region)
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
