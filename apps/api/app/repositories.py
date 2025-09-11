from __future__ import annotations

from typing import Generic, Iterable, TypeVar

from sqlalchemy.orm import Session

from app.models import (
    assets,
    controls,
    results,
    documents,
    actors,
    vendors,
    exceptions,
    users,
    meta,
)
from app.models.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository(Generic[ModelType]):
    """Generic repository providing basic CRUD operations."""

    model: type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def get(self, obj_id: int) -> ModelType | None:
        return self.session.get(self.model, obj_id)

    def list(self) -> Iterable[ModelType]:
        return self.session.query(self.model).all()

    def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> None:
        obj = self.get(obj_id)
        if obj is not None:
            self.session.delete(obj)
            self.session.commit()


class AssetRepository(SQLAlchemyRepository[assets.Asset]):
    model = assets.Asset


class ControlRepository(SQLAlchemyRepository[controls.Control]):
    model = controls.Control


class ResultRepository(SQLAlchemyRepository[results.Result]):
    model = results.Result


class DocumentRepository(SQLAlchemyRepository[documents.Document]):
    model = documents.Document


class ActorRepository(SQLAlchemyRepository[actors.Actor]):
    model = actors.Actor


class VendorRepository(SQLAlchemyRepository[vendors.Vendor]):
    model = vendors.Vendor


class ExceptionRepository(SQLAlchemyRepository[exceptions.Exception]):
    model = exceptions.Exception


class MetaRepository(SQLAlchemyRepository[meta.Meta]):
    model = meta.Meta


class UserRepository(SQLAlchemyRepository[users.User]):
    model = users.User
