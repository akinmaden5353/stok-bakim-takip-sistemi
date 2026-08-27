from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# ==========================================
# INVENTORY SCHEMAS
# ==========================================
class InventoryBase(BaseModel):
    part_code: str = Field(..., min_length=1, max_length=50, description="Benzersiz Parça Kodu")
    part_name: str = Field(..., min_length=1, max_length=150, description="Parça Adı")
    category: str = Field(default="Genel", max_length=50)
    stock_quantity: int = Field(default=0, ge=0, description="Mevcut Stok Miktarı")
    critical_level: int = Field(default=5, ge=0, description="Kritik Stok Seviyesi")
    unit: str = Field(default="Adet", max_length=20)
    unit_price: float = Field(default=0.0, ge=0.0)
    shelf_location: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    part_code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    part_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    category: Optional[str] = None
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    critical_level: Optional[int] = Field(default=None, ge=0)
    unit: Optional[str] = None
    unit_price: Optional[float] = Field(default=None, ge=0.0)
    shelf_location: Optional[str] = None
    notes: Optional[str] = None

class InventoryAdjustStock(BaseModel):
    adjustment: int = Field(..., description="Stok değişim miktarı (+ ekleme, - düşme)")
    reason: Optional[str] = Field(default="Manuel Ayarlama", description="Açıklama")

class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_critical: bool = False
    created_at: datetime
    updated_at: datetime


# ==========================================
# MACHINE SCHEMAS
# ==========================================
class MachineBase(BaseModel):
    machine_code: str = Field(..., min_length=1, max_length=50, description="Makine Kodu / Etiket")
    name: str = Field(..., min_length=1, max_length=150, description="Makine Adı")
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=100)
    last_maintenance_date: Optional[date] = None
    maintenance_interval_days: int = Field(default=30, ge=1, description="Periyodik Bakım Aralığı (Gün)")
    status: str = Field(default="Aktif", max_length=30)
    notes: Optional[str] = None

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    machine_code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    last_maintenance_date: Optional[date] = None
    maintenance_interval_days: Optional[int] = Field(default=None, ge=1)
    status: Optional[str] = None
    notes: Optional[str] = None

class MachineResponse(MachineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    next_maintenance_date: Optional[date] = None
    days_until_next_maintenance: Optional[int] = None
    maintenance_status_flag: str = "normal"  # "overdue", "upcoming", "ok"
    created_at: datetime
    updated_at: datetime


# ==========================================
# MAINTENANCE LOG SCHEMAS
# ==========================================
class MaintenanceLogBase(BaseModel):
    machine_id: int = Field(..., description="Makine ID")
    part_id: Optional[int] = Field(default=None, description="Kullanılan Yedek Parça ID (Varsa)")
    quantity_used: int = Field(default=0, ge=0, description="Kullanılan Parça Adedi")
    maintenance_date: date = Field(default_factory=date.today, description="Bakım Yapıldığı Tarih")
    maintenance_type: str = Field(default="Periyodik Bakım", max_length=50)
    technician: str = Field(..., min_length=1, max_length=100, description="Bakımı Yapan Teknisyen")
    description: str = Field(..., min_length=1, description="Yapılan İşlem ve Açıklama")
    labor_hours: Optional[float] = Field(default=1.0, ge=0.0)
    cost: Optional[float] = Field(default=0.0, ge=0.0)

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLogResponse(MaintenanceLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_name: Optional[str] = None
    machine_code: Optional[str] = None
    part_name: Optional[str] = None
    part_code: Optional[str] = None
    created_at: datetime


# ==========================================
# DETAIL RESPONSES
# ==========================================
class MachineDetailResponse(MachineResponse):
    maintenance_logs: List[MaintenanceLogResponse] = []


# ==========================================
# DASHBOARD SCHEMAS
# ==========================================
class CriticalPartAlert(BaseModel):
    id: int
    part_code: str
    part_name: str
    stock_quantity: int
    critical_level: int
    unit: str
    deficit: int

class UpcomingMaintenanceAlert(BaseModel):
    machine_id: int
    machine_code: str
    machine_name: str
    location: Optional[str]
    next_maintenance_date: date
    days_left: int
    is_overdue: bool

class DashboardKPIs(BaseModel):
    total_machines: int
    active_machines: int
    machines_needing_maintenance: int
    total_parts: int
    critical_parts_count: int
    total_maintenances_this_month: int

class DashboardSummaryResponse(BaseModel):
    kpis: DashboardKPIs
    critical_parts: List[CriticalPartAlert]
    upcoming_maintenances: List[UpcomingMaintenanceAlert]
    recent_logs: List[MaintenanceLogResponse]
