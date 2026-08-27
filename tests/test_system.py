import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import Machine, InventoryItem, MaintenanceLog
from app.services import maintenance_service, machine_service, inventory_service, dashboard_service
from app.schemas import MaintenanceLogCreate, MachineCreate, InventoryCreate
from main import app

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_machine_and_inventory_creation():
    db = TestingSessionLocal()
    # 1. Create Machine
    m_data = MachineCreate(
        machine_code="TEST-01",
        name="Test Makinesi",
        model="Model-X",
        maintenance_interval_days=15,
        status="Aktif"
    )
    m = machine_service.create_machine(db, m_data)
    assert m.id is not None
    assert m.machine_code == "TEST-01"

    # 2. Create Spare Part
    p_data = InventoryCreate(
        part_code="PART-01",
        part_name="Test Kontaktör",
        category="Elektrik",
        stock_quantity=10,
        critical_level=3,
        unit="Adet",
        unit_price=100.0
    )
    p = inventory_service.create_part(db, p_data)
    assert p.id is not None
    assert p.stock_quantity == 10
    assert p.is_critical is False
    db.close()

def test_automatic_stock_deduction_and_maintenance_scheduling():
    db = TestingSessionLocal()
    today = date.today()

    # 1. Setup machine and part
    m = machine_service.create_machine(db, MachineCreate(
        machine_code="CNC-01",
        name="CNC Torna",
        maintenance_interval_days=30,
        status="Bakımda"
    ))

    p = inventory_service.create_part(db, InventoryCreate(
        part_code="RELAY-24V",
        part_name="24V Röle",
        category="Elektrik",
        stock_quantity=5,
        critical_level=2,
        unit="Adet",
        unit_price=50.0
    ))

    # 2. Add maintenance log using 2 units of part
    log_data = MaintenanceLogCreate(
        machine_id=m.id,
        part_id=p.id,
        quantity_used=2,
        maintenance_date=today,
        maintenance_type="Periyodik Bakım",
        technician="Ali Usta",
        description="Röle arızası giderildi ve periyodik kontrol yapıldı."
    )
    log_resp = maintenance_service.create_maintenance_log(db, log_data)

    # 3. Assertions
    # A) Stock deduction check
    updated_part = inventory_service.get_part_by_id(db, p.id)
    assert updated_part.stock_quantity == 3, f"Beklenen stok 3, bulunan: {updated_part.stock_quantity}"

    # B) Machine status and date update check
    updated_machine = machine_service.get_machine_by_id(db, m.id)
    assert updated_machine.last_maintenance_date == today
    assert updated_machine.next_maintenance_date == today + timedelta(days=30)
    assert updated_machine.status == "Aktif"  # Was 'Bakımda', should now be 'Aktif'
    db.close()

def test_insufficient_stock_prevention():
    db = TestingSessionLocal()
    today = date.today()

    m = machine_service.create_machine(db, MachineCreate(
        machine_code="PRES-01",
        name="Hidrolik Pres",
        maintenance_interval_days=60
    ))

    p = inventory_service.create_part(db, InventoryCreate(
        part_code="VALVE-01",
        part_name="Hidrolik Valf",
        stock_quantity=2,
        critical_level=1,
        unit="Adet"
    ))

    # Attempt to use 5 units when only 2 exist
    log_data = MaintenanceLogCreate(
        machine_id=m.id,
        part_id=p.id,
        quantity_used=5,
        maintenance_date=today,
        technician="Veli Usta",
        description="Valf değişimi"
    )

    with pytest.raises(Exception) as exc_info:
        maintenance_service.create_maintenance_log(db, log_data)

    assert "Yetersiz Stok" in str(exc_info.value)

    # Verify stock remained untouched at 2
    unchanged_part = inventory_service.get_part_by_id(db, p.id)
    assert unchanged_part.stock_quantity == 2
    db.close()

def test_critical_stock_and_upcoming_maintenance_alerts():
    db = TestingSessionLocal()
    today = date.today()

    # Part below critical level
    p = inventory_service.create_part(db, InventoryCreate(
        part_code="CRIT-01",
        part_name="Kritik Sigorta",
        stock_quantity=1,
        critical_level=4,
        unit="Adet"
    ))

    # Machine with overdue maintenance
    m = machine_service.create_machine(db, MachineCreate(
        machine_code="OVERDUE-01",
        name="Gecikmiş Makine",
        last_maintenance_date=today - timedelta(days=40),
        maintenance_interval_days=30
    ))

    summary = dashboard_service.get_dashboard_summary(db)

    # Check KPIs and alerts
    assert summary.kpis.critical_parts_count >= 1
    assert any(alert.part_code == "CRIT-01" for alert in summary.critical_parts)

    assert summary.kpis.machines_needing_maintenance >= 1
    assert any(m_alert.machine_code == "OVERDUE-01" for m_alert in summary.upcoming_maintenances)
    db.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
