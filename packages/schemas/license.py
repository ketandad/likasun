from datetime import date
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class License(BaseModel):
    org: str
    edition: str
    features: List[str]
    seats: int
    expiry: date
    jti: UUID
    iat: int
    scope: Optional[Dict[str, List[str]]] = None
    sig: str


__all__ = ["License"]
