from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Machine, InventoryItem, MaintenanceLog
from app.schemas import (
    DashboardSummaryResponse,
    DashboardKPIs,
    CriticalPartAlert,
    UpcomingMaintenanceAlert,
    MaintenanceLogResponse
)
from app.services.maintenance_service import get_maintenance_logs
from app.config import UPCOMING_MAINTENANCE_DAYS_THRESHOLD

def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    today = date.today()
    threshold_date = today + timedelta(days=UPCOMING_MAINTENANCE_DAYS_THRESHOLD)

    # 1. Total & Active Machines
    total_machines = db.query(func.count(Machine.id)).scalar() or 0
    active_machines = db.query(func.count(Machine.id)).filter(Machine.status == "Aktif").scalar() or 0

    # 2. Upcoming & Overdue Maintenances
    upcoming_query = db.query(Machine).filter(
        (Machine.next_maintenance_date != None) &
        (Machine.next_maintenance_date <= threshold_date)
    ).order_by(Machine.next_maintenance_date.asc()).all()

    upcoming_alerts: List[UpcomingMaintenanceAlert] = []
    for m in upcoming_query:
        days_left = (m.next_maintenance_date - today).days if m.next_maintenance_date else 0
        upcoming_alerts.append(UpcomingMaintenanceAlert(
            machine_id=m.id,
            machine_code=m.machine_code,
            machine_name=m.name,
            location=m.location,
            next_maintenance_date=m.next_maintenance_date,
            days_left=days_left,
            is_overdue=(days_left < 0)
        ))

    # 3. Inventory & Critical Parts
    total_parts = db.query(func.count(InventoryItem.id)).scalar() or 0
    critical_query = db.query(InventoryItem).filter(
        InventoryItem.stock_quantity <= InventoryItem.critical_level
    ).order_by((InventoryItem.stock_quantity - InventoryItem.critical_level).asc()).all()

    critical_alerts: List[CriticalPartAlert] = []
    for p in critical_query:
        deficit = max(0, p.critical_level - p.stock_quantity)
        critical_alerts.append(CriticalPartAlert(
            id=p.id,
            part_code=p.part_code,
            part_name=p.part_name,
            stock_quantity=p.stock_quantity,
            critical_level=p.critical_level,
            unit=p.unit,
            deficit=deficit
        ))

    # 4. Maintenances this month
    current_year = today.year
    current_month = today.month
    maintenances_this_month = db.query(func.count(MaintenanceLog.id)).filter(
        extract('year', MaintenanceLog.maintenance_date) == current_year,
        extract('month', MaintenanceLog.maintenance_date) == current_month
    ).scalar() or 0

    # 5. Recent Logs (Top 6)
    recent_logs = get_maintenance_logs(db, limit=6)

    kpis = DashboardKPIs(
        total_machines=total_machines,
        active_machines=active_machines,
        machines_needing_maintenance=len(upcoming_alerts),
        total_parts=total_parts,
        critical_parts_count=len(critical_alerts),
        total_maintenances_this_month=maintenances_this_month
    )

    return DashboardSummaryResponse(
        kpis=kpis,
        critical_parts=critical_alerts,
        upcoming_maintenances=upcoming_alerts,
        recent_logs=recent_logs
    )

def get_chart_data(db: Session) -> Dict[str, Any]:
    """Generates monthly maintenance counts and top used spare parts for Chart.js."""
    today = date.today()
    months_labels = []
    monthly_counts = []

    # Last 6 months trend
    for i in range(5, -1, -1):
        # Calculate year and month
        m_offset = today.month - i
        y = today.year
        if m_offset <= 0:
            m_offset += 12
            y -= 1
        
        month_name = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"][m_offset - 1]
        months_labels.append(f"{month_name} {y}")

        count = db.query(func.count(MaintenanceLog.id)).filter(
            extract('year', MaintenanceLog.maintenance_date) == y,
            extract('month', MaintenanceLog.maintenance_date) == m_offset
        ).scalar() or 0
        monthly_counts.append(count)

    # Top used parts
    top_parts_query = db.query(
        InventoryItem.part_name,
        func.sum(MaintenanceLog.quantity_used).label("total_used")
    ).join(MaintenanceLog, InventoryItem.id == MaintenanceLog.part_id)\
     .group_by(InventoryItem.id)\
     .order_by(func.sum(MaintenanceLog.quantity_used).desc())\
     .limit(5).all()

    top_parts_labels = [row[0] for row in top_parts_query]
    top_parts_values = [row[1] for row in top_parts_query]

    return {
        "monthly": {
            "labels": months_labels,
            "data": monthly_counts
        },
        "top_parts": {
            "labels": top_parts_labels if top_parts_labels else ["Kayıt Yok"],
            "data": top_parts_values if top_parts_values else [0]
        }
    }
