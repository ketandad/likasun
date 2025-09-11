from __future__ import annotations

from .base import Connector


def get_connector(cloud: str) -> Connector:
    """Return connector instance for given cloud."""
    if cloud == "aws":
        from .aws import AWSConnector

        return AWSConnector()
    if cloud == "azure":
        from .azure import AzureConnector

        return AzureConnector()
    if cloud == "gcp":
        from .gcp import GCPConnector

        return GCPConnector()
    raise ValueError(f"Unsupported cloud '{cloud}'")
