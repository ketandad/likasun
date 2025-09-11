from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from app.models.assets import Asset


class Connector(ABC):
    """Base connector interface for cloud providers."""

    @abstractmethod
    def list_assets(self) -> List[Asset]:
        """Return a list of normalized assets."""
        raise NotImplementedError

    @abstractmethod
    def validate_permissions(self) -> Dict[str, bool]:
        """Check required permissions and return mapping of permission -> granted."""
        raise NotImplementedError
