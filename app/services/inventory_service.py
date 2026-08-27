from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import InventoryItem
from app.schemas import InventoryCreate, InventoryUpdate, InventoryAdjustStock, InventoryResponse

def get_inventory(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    only_critical: bool = False
) -> List[InventoryResponse]:
    query = db.query(InventoryItem)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (InventoryItem.part_code.ilike(search_term)) |
            (InventoryItem.part_name.ilike(search_term)) |
            (InventoryItem.category.ilike(search_term)) |
            (InventoryItem.shelf_location.ilike(search_term))
        )
    if category and category != "Tümü":
        query = query.filter(InventoryItem.category == category)
    if only_critical:
        query = query.filter(InventoryItem.stock_quantity <= InventoryItem.critical_level)

    items = query.order_by(
        (InventoryItem.stock_quantity <= InventoryItem.critical_level).desc(),
        InventoryItem.part_name.asc()
    ).all()

    results = []
    for item in items:
        resp = InventoryResponse(
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
        results.append(resp)
    return results

def get_part_by_id(db: Session, part_id: int) -> InventoryItem:
    item = db.query(InventoryItem).filter(InventoryItem.id == part_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{part_id} ID'li yedek parça bulunamadı."
        )
    return item

def create_part(db: Session, payload: InventoryCreate) -> InventoryResponse:
    existing = db.query(InventoryItem).filter(InventoryItem.part_code == payload.part_code.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{payload.part_code}' kodlu yedek parça zaten mevcut!"
        )

    db_item = InventoryItem(
        part_code=payload.part_code.strip().upper(),
        part_name=payload.part_name.strip(),
        category=payload.category.strip() if payload.category else "Genel",
        stock_quantity=payload.stock_quantity,
        critical_level=payload.critical_level,
        unit=payload.unit.strip() if payload.unit else "Adet",
        unit_price=payload.unit_price,
        shelf_location=payload.shelf_location.strip() if payload.shelf_location else None,
        notes=payload.notes
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return InventoryResponse(
        id=db_item.id,
        part_code=db_item.part_code,
        part_name=db_item.part_name,
        category=db_item.category,
        stock_quantity=db_item.stock_quantity,
        critical_level=db_item.critical_level,
        unit=db_item.unit,
        unit_price=db_item.unit_price,
        shelf_location=db_item.shelf_location,
        notes=db_item.notes,
        is_critical=(db_item.stock_quantity <= db_item.critical_level),
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )

def update_part(db: Session, part_id: int, payload: InventoryUpdate) -> InventoryResponse:
    db_item = get_part_by_id(db, part_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "part_code" in update_data and update_data["part_code"]:
        new_code = update_data["part_code"].strip().upper()
        existing = db.query(InventoryItem).filter(InventoryItem.part_code == new_code, InventoryItem.id != part_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{new_code}' kodlu başka bir yedek parça zaten mevcut!"
            )
        db_item.part_code = new_code

    for key, value in update_data.items():
        if key != "part_code":
            setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)

    return InventoryResponse(
        id=db_item.id,
        part_code=db_item.part_code,
        part_name=db_item.part_name,
        category=db_item.category,
        stock_quantity=db_item.stock_quantity,
        critical_level=db_item.critical_level,
        unit=db_item.unit,
        unit_price=db_item.unit_price,
        shelf_location=db_item.shelf_location,
        notes=db_item.notes,
        is_critical=(db_item.stock_quantity <= db_item.critical_level),
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )

def adjust_stock(db: Session, part_id: int, payload: InventoryAdjustStock) -> InventoryResponse:
    db_item = get_part_by_id(db, part_id)
    new_quantity = db_item.stock_quantity + payload.adjustment
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stok miktarı negatif olamaz! Mevcut: {db_item.stock_quantity}, İstenen Değişim: {payload.adjustment}"
        )
    db_item.stock_quantity = new_quantity
    db.commit()
    db.refresh(db_item)

    return InventoryResponse(
        id=db_item.id,
        part_code=db_item.part_code,
        part_name=db_item.part_name,
        category=db_item.category,
        stock_quantity=db_item.stock_quantity,
        critical_level=db_item.critical_level,
        unit=db_item.unit,
        unit_price=db_item.unit_price,
        shelf_location=db_item.shelf_location,
        notes=db_item.notes,
        is_critical=(db_item.stock_quantity <= db_item.critical_level),
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )

def delete_part(db: Session, part_id: int):
    db_item = get_part_by_id(db, part_id)
    db.delete(db_item)
    db.commit()
    return {"message": f"{db_item.part_name} başarıyla silindi."}
