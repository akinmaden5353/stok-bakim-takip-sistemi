from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import MaintenanceLog, Machine, InventoryItem
from app.schemas import MaintenanceLogCreate, MaintenanceLogResponse

def get_maintenance_logs(
    db: Session,
    machine_id: Optional[int] = None,
    part_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 100
) -> List[MaintenanceLogResponse]:
    query = db.query(MaintenanceLog)

    if machine_id:
        query = query.filter(MaintenanceLog.machine_id == machine_id)
    if part_id:
        query = query.filter(MaintenanceLog.part_id == part_id)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.join(Machine, MaintenanceLog.machine_id == Machine.id, isouter=True)\
                     .join(InventoryItem, MaintenanceLog.part_id == InventoryItem.id, isouter=True)\
                     .filter(
                         (MaintenanceLog.description.ilike(search_term)) |
                         (MaintenanceLog.technician.ilike(search_term)) |
                         (MaintenanceLog.maintenance_type.ilike(search_term)) |
                         (Machine.name.ilike(search_term)) |
                         (Machine.machine_code.ilike(search_term)) |
                         (InventoryItem.part_name.ilike(search_term))
                     )

    logs = query.order_by(MaintenanceLog.maintenance_date.desc(), MaintenanceLog.id.desc()).limit(limit).all()

    results = []
    for log in logs:
        resp = MaintenanceLogResponse(
            id=log.id,
            machine_id=log.machine_id,
            machine_name=log.machine.name if log.machine else "Bilinmiyor",
            machine_code=log.machine.machine_code if log.machine else "-",
            part_id=log.part_id,
            part_name=log.part.part_name if log.part else None,
            part_code=log.part.part_code if log.part else None,
            quantity_used=log.quantity_used,
            maintenance_date=log.maintenance_date,
            maintenance_type=log.maintenance_type,
            technician=log.technician,
            description=log.description,
            labor_hours=log.labor_hours,
            cost=log.cost,
            created_at=log.created_at
        )
        results.append(resp)
    return results

def create_maintenance_log(db: Session, payload: MaintenanceLogCreate) -> MaintenanceLogResponse:
    """
    Creates a new maintenance log entry with atomic business logic:
    1. Validates machine exists.
    2. If a spare part is selected and quantity > 0:
       - Checks stock availability.
       - Automatically deducts the used quantity from inventory.
    3. Updates the machine's last_maintenance_date and recalculates next_maintenance_date.
    4. Records the maintenance log.
    """
    # 1. Check Machine
    machine = db.query(Machine).filter(Machine.id == payload.machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{payload.machine_id} ID'li makine bulunamadı."
        )

    # 2. Check Part & Automatic Stock Deduction
    part = None
    if payload.part_id and payload.quantity_used > 0:
        part = db.query(InventoryItem).filter(InventoryItem.id == payload.part_id).first()
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{payload.part_id} ID'li yedek parça bulunamadı."
            )

        if part.stock_quantity < payload.quantity_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Yetersiz Stok! '{part.part_name}' ({part.part_code}) için mevcut stok: "
                    f"{part.stock_quantity} {part.unit}, ancak bakıma girilmek istenen: "
                    f"{payload.quantity_used} {part.unit}."
                )
            )

        # Atomic stock deduction
        part.stock_quantity -= payload.quantity_used

    # 3. Calculate Cost if not provided but part used
    total_cost = payload.cost or 0.0
    if part and total_cost == 0.0 and payload.quantity_used > 0:
        total_cost = part.unit_price * payload.quantity_used

    # 4. Update Machine Maintenance Dates & Status
    m_date = payload.maintenance_date or date.today()
    machine.last_maintenance_date = m_date
    machine.next_maintenance_date = m_date + timedelta(days=machine.maintenance_interval_days)

    if machine.status in ["Bakımda", "Arızalı"]:
        machine.status = "Aktif"

    # 5. Create Maintenance Log Record
    db_log = MaintenanceLog(
        machine_id=payload.machine_id,
        part_id=payload.part_id if payload.quantity_used > 0 else None,
        quantity_used=payload.quantity_used if payload.part_id else 0,
        maintenance_date=m_date,
        maintenance_type=payload.maintenance_type,
        technician=payload.technician.strip(),
        description=payload.description.strip(),
        labor_hours=payload.labor_hours,
        cost=total_cost
    )

    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return MaintenanceLogResponse(
        id=db_log.id,
        machine_id=machine.id,
        machine_name=machine.name,
        machine_code=machine.machine_code,
        part_id=part.id if part else None,
        part_name=part.part_name if part else None,
        part_code=part.part_code if part else None,
        quantity_used=db_log.quantity_used,
        maintenance_date=db_log.maintenance_date,
        maintenance_type=db_log.maintenance_type,
        technician=db_log.technician,
        description=db_log.description,
        labor_hours=db_log.labor_hours,
        cost=db_log.cost,
        created_at=db_log.created_at
    )

def delete_maintenance_log(db: Session, log_id: int, restore_stock: bool = False):
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{log_id} ID'li bakım kaydı bulunamadı."
        )

    if restore_stock and log.part_id and log.quantity_used > 0:
        part = db.query(InventoryItem).filter(InventoryItem.id == log.part_id).first()
        if part:
            part.stock_quantity += log.quantity_used

    db.delete(log)
    db.commit()
    return {"message": "Bakım kaydı başarıyla silindi."}
