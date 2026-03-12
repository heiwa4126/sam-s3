"""
Type definitions for samconfig.toml

AWS SAM CLI の設定ファイル（samconfig.toml）の構造を表す型定義を提供します。

参考:

- https://raw.githubusercontent.com/aws/aws-sam-cli/master/schema/samcli.json
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-config.html
"""

from __future__ import annotations

from typing import TypedDict


class CommandParameters(TypedDict, total=False):
    """
    SAM CLIコマンドのパラメータを表す型。

    各コマンド（build, deploy, local_start_api など）のパラメータは
    任意のキーと値を持つディクショナリとして定義されます。
    パラメータの値は文字列、整数、ブール値、リスト、またはネストされた
    ディクショナリのいずれかを取ることができます。
    """

    pass  # 任意のパラメータを受け付ける


class CommandConfig(TypedDict, total=False):
    """
    SAM CLIコマンドの設定を表す型。

    各コマンドセクションは `parameters` キーを持つことができ、
    その値は `CommandParameters` の型を持ちます。

    例:
        {
            "parameters": {
                "cached": true,
                "parallel": true
            }
        }
    """

    parameters: CommandParameters


class EnvironmentParameters(TypedDict, total=False):
    """
    環境のグローバルパラメータを表す型。

    グローバルセクションで定義されるパラメータ（stack_name, region など）
    """

    stack_name: str
    region: str


class EnvironmentGlobalConfig(TypedDict, total=False):
    """
    環境のグローバル設定セクションを表す型。
    """

    parameters: EnvironmentParameters


class SAMConfig(TypedDict, total=False):
    """
    samconfig.toml 全体の構造を表す型。

    samconfig.toml は以下の構成を持ちます:
    - version: 設定ファイルのバージョン（デフォルト 0.1）
    - 環境別設定（default, prod など）のディクショナリ

    SAMConfig は環境ごとに任意のキーを持つことができ、
    各環境はサブ環境として EnvironmentConfig として解釈されます。

    例:
        {
            "version": 0.1,
            "default": {
                "global": {"parameters": {"stack_name": "my-stack", ...}},
                "build": {"parameters": {"cached": true, ...}},
                ...
            }
        }
    """

    version: float


__all__ = [
    "CommandParameters",
    "CommandConfig",
    "EnvironmentParameters",
    "EnvironmentGlobalConfig",
    "SAMConfig",
]
