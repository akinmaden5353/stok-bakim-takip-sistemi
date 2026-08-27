from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MachineCreate, MachineUpdate, MachineResponse
from app.services import machine_service

router = APIRouter(prefix="/api/machines", tags=["Makineler"])

@router.get("", response_model=List[MachineResponse])
def read_machines(
    search: Optional[str] = Query(None, description="Arama kelimesi"),
    status: Optional[str] = Query(None, description="Durum filtresi"),
    db: Session = Depends(get_db)
):
    return machine_service.get_machines(db, search=search, status_filter=status)

@router.get("/{machine_id}", response_model=MachineResponse)
def read_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = machine_service.get_machine_by_id(db, machine_id)
    calc = machine_service.calculate_maintenance_fields(machine)
    return MachineResponse(
        id=machine.id,
        machine_code=machine.machine_code,
        name=machine.name,
        model=machine.model,
        serial_number=machine.serial_number,
        location=machine.location,
        last_maintenance_date=machine.last_maintenance_date,
        maintenance_interval_days=machine.maintenance_interval_days,
        next_maintenance_date=calc["next_maintenance_date"],
        days_until_next_maintenance=calc["days_until_next_maintenance"],
        maintenance_status_flag=calc["maintenance_status_flag"],
        status=machine.status,
        notes=machine.notes,
        created_at=machine.created_at,
        updated_at=machine.updated_at
    )

@router.post("", response_model=MachineResponse)
def create_new_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    return machine_service.create_machine(db, payload)

@router.put("/{machine_id}", response_model=MachineResponse)
def update_existing_machine(machine_id: int, payload: MachineUpdate, db: Session = Depends(get_db)):
    return machine_service.update_machine(db, machine_id, payload)

@router.delete("/{machine_id}")
def delete_existing_machine(machine_id: int, db: Session = Depends(get_db)):
    return machine_service.delete_machine(db, machine_id)
