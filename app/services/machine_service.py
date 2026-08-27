from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Machine, MaintenanceLog
from app.schemas import MachineCreate, MachineUpdate, MachineResponse

def calculate_maintenance_fields(machine: Machine) -> dict:
    """Calculates next_maintenance_date, days_left, and maintenance_status_flag."""
    today = date.today()
    next_date = machine.next_maintenance_date
    if not next_date and machine.last_maintenance_date:
        next_date = machine.last_maintenance_date + timedelta(days=machine.maintenance_interval_days)
    elif not next_date and not machine.last_maintenance_date:
        next_date = today

    days_until = (next_date - today).days if next_date else None

    flag = "ok"
    if days_until is not None:
        if days_until < 0:
            flag = "overdue"
        elif days_until <= 7:
            flag = "upcoming"
        else:
            flag = "ok"

    return {
        "next_maintenance_date": next_date,
        "days_until_next_maintenance": days_until,
        "maintenance_status_flag": flag
    }

def get_machines(db: Session, search: Optional[str] = None, status_filter: Optional[str] = None) -> List[MachineResponse]:
    query = db.query(Machine)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Machine.machine_code.ilike(search_term)) |
            (Machine.name.ilike(search_term)) |
            (Machine.model.ilike(search_term)) |
            (Machine.location.ilike(search_term))
        )
    if status_filter and status_filter != "Tümü":
        query = query.filter(Machine.status == status_filter)

    machines = query.order_by(Machine.next_maintenance_date.asc().nullsfirst()).all()
    results = []
    for m in machines:
        calc = calculate_maintenance_fields(m)
        m_dict = {
            "id": m.id,
            "machine_code": m.machine_code,
            "name": m.name,
            "model": m.model,
            "serial_number": m.serial_number,
            "location": m.location,
            "last_maintenance_date": m.last_maintenance_date,
            "maintenance_interval_days": m.maintenance_interval_days,
            "next_maintenance_date": calc["next_maintenance_date"],
            "days_until_next_maintenance": calc["days_until_next_maintenance"],
            "maintenance_status_flag": calc["maintenance_status_flag"],
            "status": m.status,
            "notes": m.notes,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }
        results.append(MachineResponse(**m_dict))
    return results

def get_machine_by_id(db: Session, machine_id: int) -> Machine:
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{machine_id} ID'li makine bulunamadı."
        )
    return machine

def create_machine(db: Session, payload: MachineCreate) -> MachineResponse:
    existing = db.query(Machine).filter(Machine.machine_code == payload.machine_code.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{payload.machine_code}' kodlu makine zaten mevcut!"
        )

    # Compute initial next_maintenance_date
    next_date = None
    if payload.last_maintenance_date:
        next_date = payload.last_maintenance_date + timedelta(days=payload.maintenance_interval_days)
    else:
        next_date = date.today() + timedelta(days=payload.maintenance_interval_days)

    db_machine = Machine(
        machine_code=payload.machine_code.strip().upper(),
        name=payload.name.strip(),
        model=payload.model.strip() if payload.model else None,
        serial_number=payload.serial_number.strip() if payload.serial_number else None,
        location=payload.location.strip() if payload.location else None,
        last_maintenance_date=payload.last_maintenance_date,
        maintenance_interval_days=payload.maintenance_interval_days,
        next_maintenance_date=next_date,
        status=payload.status,
        notes=payload.notes
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)

    calc = calculate_maintenance_fields(db_machine)
    return MachineResponse(
        id=db_machine.id,
        machine_code=db_machine.machine_code,
        name=db_machine.name,
        model=db_machine.model,
        serial_number=db_machine.serial_number,
        location=db_machine.location,
        last_maintenance_date=db_machine.last_maintenance_date,
        maintenance_interval_days=db_machine.maintenance_interval_days,
        next_maintenance_date=calc["next_maintenance_date"],
        days_until_next_maintenance=calc["days_until_next_maintenance"],
        maintenance_status_flag=calc["maintenance_status_flag"],
        status=db_machine.status,
        notes=db_machine.notes,
        created_at=db_machine.created_at,
        updated_at=db_machine.updated_at,
    )

def update_machine(db: Session, machine_id: int, payload: MachineUpdate) -> MachineResponse:
    db_machine = get_machine_by_id(db, machine_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "machine_code" in update_data and update_data["machine_code"]:
        new_code = update_data["machine_code"].strip().upper()
        existing = db.query(Machine).filter(Machine.machine_code == new_code, Machine.id != machine_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{new_code}' kodlu başka bir makine zaten mevcut!"
            )
        db_machine.machine_code = new_code

    for key, value in update_data.items():
        if key != "machine_code":
            setattr(db_machine, key, value)

    # Recalculate next maintenance date if interval or last maintenance changed
    if "last_maintenance_date" in update_data or "maintenance_interval_days" in update_data:
        if db_machine.last_maintenance_date:
            db_machine.next_maintenance_date = db_machine.last_maintenance_date + timedelta(days=db_machine.maintenance_interval_days)

    db.commit()
    db.refresh(db_machine)

    calc = calculate_maintenance_fields(db_machine)
    return MachineResponse(
        id=db_machine.id,
        machine_code=db_machine.machine_code,
        name=db_machine.name,
        model=db_machine.model,
        serial_number=db_machine.serial_number,
        location=db_machine.location,
        last_maintenance_date=db_machine.last_maintenance_date,
        maintenance_interval_days=db_machine.maintenance_interval_days,
        next_maintenance_date=calc["next_maintenance_date"],
        days_until_next_maintenance=calc["days_until_next_maintenance"],
        maintenance_status_flag=calc["maintenance_status_flag"],
        status=db_machine.status,
        notes=db_machine.notes,
        created_at=db_machine.created_at,
        updated_at=db_machine.updated_at,
    )

def delete_machine(db: Session, machine_id: int):
    db_machine = get_machine_by_id(db, machine_id)
    db.delete(db_machine)
    db.commit()
    return {"message": f"{db_machine.name} başarıyla silindi."}
