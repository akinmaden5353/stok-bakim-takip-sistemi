from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import InventoryCreate, InventoryUpdate, InventoryAdjustStock, InventoryResponse
from app.services import inventory_service

router = APIRouter(prefix="/api/inventory", tags=["Yedek Parça ve Stok"])

@router.get("", response_model=List[InventoryResponse])
def read_inventory(
    search: Optional[str] = Query(None, description="Arama"),
    category: Optional[str] = Query(None, description="Kategori"),
    only_critical: bool = Query(False, description="Sadece kritik seviyedekiler"),
    db: Session = Depends(get_db)
):
    return inventory_service.get_inventory(db, search=search, category=category, only_critical=only_critical)

@router.get("/{part_id}", response_model=InventoryResponse)
def read_part(part_id: int, db: Session = Depends(get_db)):
    item = inventory_service.get_part_by_id(db, part_id)
    return InventoryResponse(
        id=item.id,
        part_code=item.part_code,
        part_name=item.part_name,
        category=item.category,
        stock_quantity=item.stock_quantity,
        critical_level=item.critical_level,
        unit=item.unit,
        unit_price=item.unit_price,
        shelf_location=item.shelf_location,
        notes=item.notes,
        is_critical=(item.stock_quantity <= item.critical_level),
        created_at=item.created_at,
        updated_at=item.updated_at
    )

@router.post("", response_model=InventoryResponse)
def create_new_part(payload: InventoryCreate, db: Session = Depends(get_db)):
    return inventory_service.create_part(db, payload)

@router.put("/{part_id}", response_model=InventoryResponse)
def update_existing_part(part_id: int, payload: InventoryUpdate, db: Session = Depends(get_db)):
    return inventory_service.update_part(db, part_id, payload)

@router.post("/{part_id}/adjust-stock", response_model=InventoryResponse)
def adjust_part_stock(part_id: int, payload: InventoryAdjustStock, db: Session = Depends(get_db)):
    return inventory_service.adjust_stock(db, part_id, payload)

@router.delete("/{part_id}")
def delete_existing_part(part_id: int, db: Session = Depends(get_db)):
    return inventory_service.delete_part(db, part_id)
