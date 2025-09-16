"""Vendors endpoints."""


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import vendors as vendor_m
from app.models.vendors import VendorModel
from app.repositories import VendorRepository

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("/", response_model=list[VendorModel])
def list_vendors(db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    vendors = repo.list()
    return [VendorModel.model_validate(v) for v in vendors]


class VendorCreate(BaseModel):
    name: str
    risk: str = "medium"
    dpa_signed: bool = False
    pii: bool = False


@router.post("/", response_model=VendorModel)
def add_vendor(data: VendorCreate, db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = vendor_m.Vendor(
        name=data.name,
        risk=data.risk,
        dpa_signed=data.dpa_signed,
        pii=data.pii,
    )
    return repo.add(vendor)


class VendorBulkCreate(BaseModel):
    vendors: list[VendorCreate]


@router.post("/bulk", response_model=list[VendorModel])
def add_vendors_bulk(data: VendorBulkCreate, db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    created = []
    for v in data.vendors:
        vendor = vendor_m.Vendor(
            name=v.name,
            risk=v.risk,
            dpa_signed=v.dpa_signed,
            pii=v.pii,
        )
        created.append(repo.add(vendor))
    return [VendorModel.model_validate(v) for v in created]

