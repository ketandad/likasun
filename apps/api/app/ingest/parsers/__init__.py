from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, List

from . import aws, azure, gcp, iac

PARSER_MAP: dict[str, Callable[[List[Path]], list[dict[str, Any]]]] = {
    "aws": aws.parse_files,
    "azure": azure.parse_files,
    "gcp": gcp.parse_files,
    "iac": iac.parse_files,
}


def get_parser(cloud: str) -> Callable[[List[Path]], list[dict[str, Any]]]:
    try:
        return PARSER_MAP[cloud]
    except KeyError as exc:
        raise ValueError(f"Unsupported cloud '{cloud}'") from exc
