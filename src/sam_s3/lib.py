from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from .config_types import CommandConfig, CommandParameters, SAMConfig

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def find_samconfig_path(file_name: str = "samconfig.toml") -> Path:
    """
    現在のディレクトリから指定されたファイルを検索し、そのパスを返す。

    現在の作業ディレクトリから開始して、親ディレクトリへと遡りながら
    指定されたファイルを検索します。最初に見つかったファイルのパスを返します。

    Args:
        file_name (str): 検索するファイル名。デフォルトは "samconfig.toml"。

    Returns:
        Path: 見つかったファイルの絶対パス。

    Raises:
        FileNotFoundError: 現在のディレクトリとその親ディレクトリ全体を検索しても
                          指定されたファイルが見つからない場合に発生します。
    """
    current = Path.cwd().resolve()

    for candidate in [current, *current.parents]:
        config_path = candidate / file_name
        if config_path.exists():
            return config_path

    raise FileNotFoundError(
        f"{file_name} was not found from current directory: {Path.cwd()}"
    )


def load_samconfig(config_path: Path) -> SAMConfig:
    """
    samconfig.toml ファイルを読み込み、SAMConfig オブジェクトとして返します。

    samconfig.toml は TOML フォーマットで記述された AWS SAM CLI の
    設定ファイルです。このファイルから全ての環境設定とコマンドパラメータを
    読み込みます。

    Args:
        config_path (Path): samconfig.toml ファイルのパス

    Returns:
        SAMConfig: 設定ファイルの内容を表す TypedDict オブジェクト

    Raises:
        FileNotFoundError: 指定されたパスにファイルが存在しない場合
        ValueError: TOML ファイルが無効な形式の場合

    Example:
        >>> from pathlib import Path
        >>> config_path = Path("samconfig.toml")
        >>> config = load_samconfig(config_path)
        >>> print(config.get("version"))
        0.1
        >>> print(config["default"]["global"]["parameters"]["stack_name"])
        "my-stack"
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open("rb") as f:
            loaded = tomllib.load(f)
        if not isinstance(loaded, dict):
            raise ValueError(f"TOML root must be a table, got {type(loaded).__name__}")
        config = cast(SAMConfig, loaded)
        return config
    except Exception as e:
        raise ValueError(f"Failed to parse TOML file {config_path}: {e}")


def get_environment_config(
    config: SAMConfig, environment: str = "default"
) -> dict[str, Any]:
    """
    SAMConfig から指定された環境の設定を取得します。

    Args:
        config (SAMConfig): load_samconfig() で読み込んだ設定
        environment (str): 環境名（デフォルト: "default"）

    Returns:
        dict[str, Any]: 指定された環境の設定

    Raises:
        KeyError: 指定された環境が設定に存在しない場合

    Example:
        >>> config = load_samconfig(Path("samconfig.toml"))
        >>> default_env = get_environment_config(config, "default")
        >>> print(default_env["global"]["parameters"]["stack_name"])
    """
    if environment not in config:
        raise KeyError(
            f"Environment '{environment}' not found in configuration. "
            f"Available environments: {list(config.keys())}"
        )

    env_config = config[environment]
    if not isinstance(env_config, dict):
        raise ValueError(
            f"Environment '{environment}' must be a table, got {type(env_config).__name__}"
        )

    return env_config


def get_command_parameters(
    env_config: dict[str, Any], command: str
) -> CommandParameters:
    """
    環境設定から指定されたコマンドのパラメータを取得します。

    Args:
        env_config (dict[str, Any]): 環境設定
        command (str): コマンド名（例: "build", "deploy", "local_start_api"）

    Returns:
        CommandParameters: コマンドのパラメータ

    Raises:
        KeyError: 指定されたコマンドが設定に存在しない場合

    Example:
        >>> config = load_samconfig(Path("samconfig.toml"))
        >>> env_config = get_environment_config(config)
        >>> deploy_params = get_command_parameters(env_config, "deploy")
        >>> print(deploy_params.get("capabilities"))
        "CAPABILITY_IAM"
    """
    if command not in env_config:
        raise KeyError(
            f"Command '{command}' not found in environment configuration. "
            f"Available commands: {[k for k in env_config.keys() if k != 'global']}"
        )

    command_config = env_config[command]
    if not isinstance(command_config, dict):
        raise ValueError(
            f"Command '{command}' config must be a table, got {type(command_config).__name__}"
        )
    return command_config.get("parameters", {})


def load_stack_and_region(
    config_path: Path, environment: str = "default"
) -> tuple[str, str]:
    """
    設定ファイルから指定された環境のスタック名とリージョンを読み込みます。

    TOMLフォーマットの設定ファイルを開き、指定された環境の設定から
    スタック名とリージョンを抽出します。スタック名はグローバルまたは
    デプロイパラメータから、リージョンはデプロイまたはグローバル
    パラメータから取得されます。

    Args:
        config_path (Path): TOML設定ファイルのパス
        environment (str, optional): 環境名。デフォルトは "default"

    Returns:
        tuple[str, str]: (スタック名, リージョン) のタプル

    Raises:
        KeyError: スタック名またはリージョンが設定ファイルに見つからない場合
    """
    config = load_samconfig(config_path)
    env_config = get_environment_config(config, environment)

    global_params = env_config.get("global", {}).get("parameters", {})
    deploy_params = env_config.get("deploy", {}).get("parameters", {})

    stack_name = global_params.get("stack_name") or deploy_params.get("stack_name")
    region = deploy_params.get("region") or global_params.get("region")

    if not stack_name:
        raise KeyError(
            f"stack_name is missing in [{environment}.global.parameters] or [{environment}.deploy.parameters]"
        )
    if not region:
        raise KeyError(
            f"region is missing in [{environment}.global.parameters] or [{environment}.deploy.parameters]"
        )

    return stack_name, region


__all__ = [
    "find_samconfig_path",
    "load_stack_and_region",
    "load_samconfig",
    "get_environment_config",
    "get_command_parameters",
    "SAMConfig",
    "CommandConfig",
    "CommandParameters",
]
