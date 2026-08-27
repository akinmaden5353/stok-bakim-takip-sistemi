from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MaintenanceLogCreate, MaintenanceLogResponse
from app.services import maintenance_service

router = APIRouter(prefix="/api/maintenance", tags=["Bakım Kayıtları"])

@router.get("", response_model=List[MaintenanceLogResponse])
def read_maintenance_logs(
    machine_id: Optional[int] = Query(None, description="Makine ID filtresi"),
    part_id: Optional[int] = Query(None, description="Parça ID filtresi"),
    search: Optional[str] = Query(None, description="Arama kelimesi"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return maintenance_service.get_maintenance_logs(
        db,
        machine_id=machine_id,
        part_id=part_id,
        search=search,
        limit=limit
    )

@router.post("", response_model=MaintenanceLogResponse)
def create_new_maintenance_log(payload: MaintenanceLogCreate, db: Session = Depends(get_db)):
    return maintenance_service.create_maintenance_log(db, payload)

@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    restore_stock: bool = Query(False, description="Kullanılan parçayı stoğa geri iade et"),
    db: Session = Depends(get_db)
):
    return maintenance_service.delete_maintenance_log(db, log_id, restore_stock=restore_stock)
